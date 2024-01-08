import rpi_sentry_core.camera as camera
import rpi_sentry_core.trigger as trigger
import rpi_sentry_core.logic as logic
from fs import open_fs
import tempfile


def main():
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        print("saving photos in", tmp_dir_name)
        fs = open_fs(tmp_dir_name)

        logic_conf = {
            "action": trigger.activate(camera.RealCamera(), fs),
            "frequency": 2,
            "pins": {"sound_sensor": 1, "motion_sensor_1": 2, "motion_sensor_2": 3},
            "weights": {
                "motion": 6,
                "sound": 4,
            },
            "window": 60,
        }

        initial_readings = {
            "motion_1": 0.0,
            "motion_2": 0.0,
            "sound": 0.0,
        }

        logic.run(logic_conf, initial_readings)
