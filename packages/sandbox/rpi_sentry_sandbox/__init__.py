import json
import os
import rpi_sentry_core.api as api
import rpi_sentry_core.trigger as trigger
import rpi_sentry_core.logic as logic
import tkgpio
from fs import open_fs
import tempfile


class FakeCamera(api.Camera):
    def shoot(self, rank, path):
        print("shooting footage with rank:", rank)
        print("saving footage at", path)


circuit_conf_path = os.path.join(os.path.dirname(__file__), "circuit.json")

with open(circuit_conf_path, "r") as file:
    circuit_conf = json.load(file)
    motion_sensors_conf = circuit_conf["motion_sensors"]

circuit = tkgpio.TkCircuit(circuit_conf)


@circuit.run
def main():
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        print("saving photos in", tmp_dir_name)
        fs = open_fs(tmp_dir_name)

        logic_conf = {
            "action": trigger.activate(FakeCamera(), fs),
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
