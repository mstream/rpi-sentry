import server

import logging
import os
import pathlib

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

if __name__ == "__main__":
    server.run(
        base_dir=pathlib.Path(__file__).parent,
        camera_logger=logging.getLogger("camera"),
        home_dir=pathlib.Path.home(),
        port=80,
        server_logger=logging.getLogger("server"),
    )
