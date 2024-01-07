import gpiozero
import math
import time

last_timestamps = {"motion_1": 0.0, "motion_2": 0.0, "sound": 0.0}


def on_sensor_triggered(sensor_name, now):
    global last_timestamps
    last_timestamps[sensor_name] = now


def rank(window, delta):
    value = window - delta
    if value <= 1:
        return 0.0
    elif value >= window:
        return 1.0
    else:
        return math.log(value, window)


def sensor_rank(window, sensor_name, now):
    delta = now - last_timestamps[sensor_name]
    return rank(window, delta)


def presence_rank(window, now):
    sound = 0.5 * sensor_rank(window, "sound", now)
    motion_1 = 0.25 * sensor_rank(window, "motion_1", now)
    motion_2 = 0.25 * sensor_rank(window, "motion_2", now)

    return sound + motion_1 + motion_2


def logic(config):
    sound_sensor = gpiozero.MotionSensor(config["pins"]["sound_sensor"])
    motion_sensor_1 = gpiozero.MotionSensor(config["pins"]["motion_sensor_1"])
    motion_sensor_2 = gpiozero.MotionSensor(config["pins"]["motion_sensor_2"])

    sound_sensor.when_motion = lambda: on_sensor_triggered("sound", time.time())
    motion_sensor_1.when_motion = lambda: on_sensor_triggered("motion_1", time.time())
    motion_sensor_2.when_motion = lambda: on_sensor_triggered("motion_2", time.time())

    sleep_time = 1.0 / config["frequency"]

    window = config["window"]

    while True:
        now = time.time()
        rank = presence_rank(window, now)
        print("rank: ", rank)
        time.sleep(sleep_time)
