from aiohttp import web
from aiohttp.web_runner import GracefulExit
import aiohttp_jinja2
import avro.io
import avro.schema
import asyncio
import camera
import io
import jinja2
import pathlib
import shutil


BASE_DIR = pathlib.Path(__file__).parent


def app_key(name):
    return f"rpisentry.{name}"


camera_key = app_key("camera")
camera_handler_key = app_key("camera_handler")
websockets_key = app_key("websockets")

with open(str(BASE_DIR / "update.avsc"), "rb") as f:
    schema = avro.schema.parse(f.read())


async def handle_camera(app: web.Application):
    try:
        print("camera init")
        camera = app[camera_key]
        while True:
            websockets = app[websockets_key]
            camera.update()
            _, _, bytes_free = shutil.disk_usage("/")
            writer = avro.io.DatumWriter(schema)
            bytes_writer = io.BytesIO()
            encoder = avro.io.BinaryEncoder(bytes_writer)
            writer.write(
                {
                    "previewImage": camera.preview_image,
                    "spaceRemaining": round(bytes_free / 2**30, 2),
                    "state": camera.state.name,
                },
                encoder,
            )
            raw_bytes = bytes_writer.getvalue()
            for ws in websockets:
                await ws.send_bytes(raw_bytes)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("camera cancelled")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
    finally:
        print("camera shutdown")
        raise GracefulExit()


async def on_startup(app: web.Application):
    app[camera_handler_key] = asyncio.create_task(handle_camera(app))


async def on_cleanup(app: web.Application):
    app[camera_handler_key].cancel()
    await app[camera_handler_key]


async def on_shutdown(app: web.Application):
    for ws in app[websockets_key]:
        await ws.close(code=999, message="Server shutdown")


@aiohttp_jinja2.template("index.html.jinja2")
async def index_handler(request: web.Request):
    return {"schemaJson": str(schema)}


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    response = web.WebSocketResponse()
    await response.prepare(request)
    request.app[websockets_key].append(response)
    try:
        print("websocket init")
        async for msg in response:
            pass
        return response
    except asyncio.CancelledError:
        print("websocker cancelled")
    finally:
        request.app[websockets_key].remove(response)
        print("websocket cleanup")


def init() -> web.Application:
    app = web.Application()
    app[websockets_key] = []
    app[camera_key] = camera.Camera(
        root_dir_path=str(pathlib.Path.home() / "footage"),
    )
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(str(BASE_DIR / "templates"))
    )
    app.router.add_get("/", index_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/static", str(BASE_DIR / "static"))
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    web.run_app(init(), port=80)
