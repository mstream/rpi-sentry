from aiohttp import web
from aiohttp.web_runner import GracefulExit
import aiohttp_jinja2
import avro.io
import avro.schema
import asyncio
from camera import Camera, Mode
import io
import jinja2
import pathlib
import shutil
import time


BASE_DIR = pathlib.Path(__file__).parent


def app_key(name):
    return f"rpisentry.{name}"


camera_key = app_key("camera")
camera_handler_key = app_key("camera_handler")
websockets_key = app_key("websockets")

with open(str(BASE_DIR / "request.avsc"), "rb") as f:
    request_schema = avro.schema.parse(f.read())
    reader = avro.io.DatumReader(request_schema)

with open(str(BASE_DIR / "update.avsc"), "rb") as f:
    update_schema = avro.schema.parse(f.read())
    writer = avro.io.DatumWriter(update_schema)


async def handle_camera(app: web.Application):
    try:
        print("camera initialized")
        camera = app[camera_key]
        while True:
            websockets = app[websockets_key]
            sensor_readings = {
                "sensor1": True,
                "sensor2": True,
                "sensor3": False,
            }
            camera.update(time.time_ns(), sensor_readings)

            if len(websockets) > 0:
                _, _, bytes_free = shutil.disk_usage("/")
                message_bytes = io.BytesIO()
                encoder = avro.io.BinaryEncoder(message_bytes)
                update_message = {
                    "afWindow": {
                        "x": camera.preview_af_window[0],
                        "y": camera.preview_af_window[1],
                        "w": camera.preview_af_window[2],
                        "h": camera.preview_af_window[3],
                    },
                    "cameraMode": camera.mode.name,
                    "previewImage": camera.preview_image,
                    "sensorReadings": sensor_readings,
                    "spaceRemaining": round(bytes_free / 2**30, 2),
                    "state": camera.state.name,
                }
                writer.write(update_message, encoder)
                raw_bytes = message_bytes.getvalue()
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
    return {
        "requestSchemaJson": str(request_schema),
        "updateSchemaJson": str(update_schema),
    }


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    response = web.WebSocketResponse()
    await response.prepare(request)
    request.app[websockets_key].append(response)
    try:
        print("websocket initialized")
        async for msg in response:
            message_bytes = io.BytesIO(msg.data)
            decoder = avro.io.BinaryDecoder(message_bytes)
            request_message = reader.read(decoder)
            match request_message:
                case "SET_CAMERA_MODE_ALWAYS_ON":
                    camera = request.app[camera_key]
                    camera.mode = Mode.ALWAYS_ON
                case "SET_CAMERA_MODE_AUTOMATIC":
                    camera = request.app[camera_key]
                    camera.mode = Mode.AUTOMATIC
                case _:
                    print(f"Unmatched request message: {request_message}")
        return response
    except asyncio.CancelledError:
        print("websocker cancelled")
    finally:
        request.app[websockets_key].remove(response)
        print("websocket cleanup")


def init() -> web.Application:
    app = web.Application()
    app[websockets_key] = []
    app[camera_key] = Camera(
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
