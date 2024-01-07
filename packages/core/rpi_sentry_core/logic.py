import gpiozero
import math
import pydantic as p
import time
import typing

last_timestamps = {"motion_1": 0.0, "motion_2": 0.0, "sound": 0.0}


class TriggerEvent(p.BaseModel):
    rank: float
    timestamp: float


class Pins(p.BaseModel):
    motion_sensor_1: p.PositiveInt
    motion_sensor_2: p.PositiveInt
    sound_sensor: p.PositiveInt


class Weights(p.BaseModel):
    motion: p.PositiveInt
    sound: p.PositiveInt


class Config(p.BaseModel):
    action: typing.Callable[[TriggerEvent], None]
    frequency: p.PositiveInt
    pins: Pins
    weights: Weights
    window: p.PositiveInt


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


def presence_rank(weight_sound_sensor, weight_motion_sensor, window, now):
    sound = weight_sound_sensor * sensor_rank(window, "sound", now)
    motion_1 = weight_motion_sensor * sensor_rank(window, "motion_1", now)
    motion_2 = weight_motion_sensor * sensor_rank(window, "motion_2", now)

    return sound + motion_1 + motion_2


def logic(external_config):
    config = Config(**external_config)
    sound_sensor = gpiozero.MotionSensor(config.pins.sound_sensor)
    motion_sensor_1 = gpiozero.MotionSensor(config.pins.motion_sensor_1)
    motion_sensor_2 = gpiozero.MotionSensor(config.pins.motion_sensor_2)

    sound_sensor.when_motion = lambda: on_sensor_triggered("sound", time.time())
    motion_sensor_1.when_motion = lambda: on_sensor_triggered("motion_1", time.time())
    motion_sensor_2.when_motion = lambda: on_sensor_triggered("motion_2", time.time())

    max_sleep_time = 1.0 / config.frequency

    weight_total = config.weights.motion + config.weights.sound
    weight_sound_sensor = config.weights.sound / weight_total
    weight_motion_sensor = (config.weights.motion / 2) / weight_total

    while True:
        now = time.time()
        rank = presence_rank(
            weight_sound_sensor, weight_motion_sensor, config.window, now
        )
        config.action(TriggerEvent(rank=rank, timestamp=now))
        time_elapsed = time.time() - now
        sleep_time = max_sleep_time - time_elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
