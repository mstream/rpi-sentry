import json
import logging
import os
import rpi_sentry_core.api as api
import rpi_sentry_core.trigger as trigger
import rpi_sentry_core.logic as logic
import time
import tkgpio
import tempfile

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))
logger = logging.getLogger(__name__)


class FakeCamera(api.Camera):
    def __init__(self, root_dir_path):
        self.root_dir_path = root_dir_path

    def create_dir(self, path):
        dir_path = os.path.join(self.root_dir_path, path.dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def shoot(self, rank, path):
        dir_path = self.create_dir(path)
        file_path = os.path.join(
            dir_path,
            f"{path.file_base_name}.dummy",
        )
        logger.info("shooting footage with %s rank", rank)
        time.sleep(1)
        logger.info("saving footage at %s", file_path)
        file = open(file_path, "w")
        file.close()


circuit_conf_path = os.path.join(os.path.dirname(__file__), "circuit.json")

with open(circuit_conf_path, "r") as file:
    circuit_conf = json.load(file)
    motion_sensors_conf = circuit_conf["motion_sensors"]

circuit = tkgpio.TkCircuit(circuit_conf)


@circuit.run
def main():
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        logic_conf = {
            "action": trigger.activate(FakeCamera(tmp_dir_path)),
            "frequency": 2,
            "pins": {
                "sound_sensor": motion_sensors_conf[0]["pin"],
                "motion_sensor_1": motion_sensors_conf[1]["pin"],
                "motion_sensor_2": motion_sensors_conf[2]["pin"],
            },
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
