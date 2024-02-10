from aiohttp import web
from aiohttp.web_runner import GracefulExit
import aiohttp_jinja2
import avro.io
import avro.schema
import asyncio
from camera import Camera, Mode
import io
import jinja2
import shutil
import time


def app_key(name):
    return f"rpisentry.{name}"


camera_key = app_key("camera")
camera_handler_key = app_key("camera_handler")
client_message_reader_key = app_key("client_message_reader")
client_message_writer_key = app_key("client_message_writer")
logger_key = app_key("logger")
request_schema_key = app_key("request_schema")
update_schema_key = app_key("update_schema")
websockets_key = app_key("websockets")


async def handle_camera(app: web.Application):
    camera = app[camera_key]
    client_message_writer = app[client_message_writer_key]
    logger = app[logger_key]
    logger.debug("Camera handler initialized")
    try:
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
                client_message_writer.write(update_message, encoder)
                raw_bytes = message_bytes.getvalue()
                for ws in websockets:
                    await ws.send_bytes(raw_bytes)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.warn("Camera handler cancelled")
    except Exception as err:
        logger.error("Unexpected camera error", exc_info=err)
    finally:
        logger.info("Shutting down")
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
    app = request.app
    request_schema = app[request_schema_key]
    update_schema = app[update_schema_key]
    return {
        "requestSchemaJson": str(request_schema),
        "updateSchemaJson": str(update_schema),
    }


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    app = request.app
    client_message_reader = app[client_message_reader_key]
    logger = app[logger_key]
    websockets = app[websockets_key]
    response = web.WebSocketResponse()
    await response.prepare(request)
    websockets.append(response)
    try:
        logger.debug("New websocket initialized")
        async for msg in response:
            message_bytes = io.BytesIO(msg.data)
            decoder = avro.io.BinaryDecoder(message_bytes)
            request_message = client_message_reader.read(decoder)
            match request_message:
                case "SET_CAMERA_MODE_ALWAYS_ON":
                    camera = request.app[camera_key]
                    camera.mode = Mode.ALWAYS_ON
                case "SET_CAMERA_MODE_AUTOMATIC":
                    camera = request.app[camera_key]
                    camera.mode = Mode.AUTOMATIC
                case _:
                    logger.error("Unmatched request message: %s", request_message)
        return response
    except asyncio.CancelledError:
        logger.warn("Websocket handler cancelled")
    finally:
        logger.info("Shutting down websocket")
        request.app[websockets_key].remove(response)


def init(base_dir, camera_logger, home_dir, server_logger) -> web.Application:
    app = web.Application()

    app[logger_key] = server_logger
    app[websockets_key] = []

    with open(str(base_dir / "request.avsc"), "rb") as f:
        request_schema = avro.schema.parse(f.read())
        reader = avro.io.DatumReader(request_schema)
        app[client_message_reader_key] = reader
        app[request_schema_key] = request_schema

    with open(str(base_dir / "update.avsc"), "rb") as f:
        update_schema = avro.schema.parse(f.read())
        writer = avro.io.DatumWriter(update_schema)
        app[client_message_writer_key] = writer
        app[update_schema_key] = update_schema

    app[camera_key] = Camera(
        logger=camera_logger,
        root_dir_path=str(home_dir / "footage"),
    )

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(str(base_dir / "templates"))
    )

    app.router.add_get("/", index_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/static", str(base_dir / "static"))
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.on_shutdown.append(on_shutdown)
    return app


def run(base_dir, camera_logger, home_dir, port, server_logger):
    web.run_app(init(base_dir, camera_logger, home_dir, server_logger), port=port)
