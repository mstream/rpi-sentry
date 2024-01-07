import json
import os
import rpi_sentry_core.logic
import tkgpio

circuit_conf_path = os.path.join(os.path.dirname(__file__), "circuit.json")


with open(circuit_conf_path, "r") as file:
    circuit_conf = json.load(file)
    motion_sensors_conf = circuit_conf["motion_sensors"]


logic_conf = {
    "action": lambda event: print("action triggered", event),
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

circuit = tkgpio.TkCircuit(circuit_conf)


@circuit.run
def main():
    rpi_sentry_core.logic.logic(logic_conf)
