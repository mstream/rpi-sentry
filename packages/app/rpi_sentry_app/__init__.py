import logging
import os
from pathlib import Path
import rpi_sentry_core.camera as camera
import rpi_sentry_core.trigger as trigger
import rpi_sentry_core.logic as logic

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


def main():
    root_dir_path = os.path.join(str(Path.home()), "footage")
    logic_conf = {
        "action": trigger.activate(camera.RealCamera(root_dir_path)),
        "frequency": 2,
        "pins": {"sound_sensor": 4, "motion_sensor_1": 17, "motion_sensor_2": 27},
        "weights": {
            "motion": 6,
            "sound": 4,
        },
        "window": 60,
    }

    initial_readings = {
        "motion_1": 2705231416070286000.0,
        "motion_2": 2705231416070286000.0,
        "sound": 2705231416070286000.0,
    }

    logic.run(logic_conf, initial_readings)


if __name__ == "__main__":
    main()
