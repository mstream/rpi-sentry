import json
import os
import rpi_sentry_core.camera
import rpi_sentry_core.logic
import tkgpio

circuit_conf_path = os.path.join(os.path.dirname(__file__), "circuit.json")


with open(circuit_conf_path, "r") as file:
    circuit_conf = json.load(file)
    motion_sensors_conf = circuit_conf["motion_sensors"]


logic_conf = {
    "action": rpi_sentry_core.camera.take_photo,
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

circuit = tkgpio.TkCircuit(circuit_conf)


@circuit.run
def main():
    rpi_sentry_core.logic.run(logic_conf, initial_readings)
