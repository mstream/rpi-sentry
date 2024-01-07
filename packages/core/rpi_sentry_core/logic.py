import gpiozero
import math
import pydantic as p
import time
import typing


def generateTimestamp():
    return time.time_ns()


def sleep(duration):
    time.sleep(duration / 1e9)


class SensorReadings(p.BaseModel):
    motion_1: float
    motion_2: float
    sound: float

    def update_motion_1(self, timestamp):
        self.motion_1 = timestamp

    def update_motion_2(self, timestamp):
        self.motion_2 = timestamp

    def update_sound(self, timestamp):
        self.sound = timestamp

    def get_motion_rank_1(self, window, now):
        return rank(window, now - self.motion_1)

    def get_motion_rank_2(self, window, now):
        return rank(window, now - self.motion_2)

    def get_sound_rank(self, window, now):
        return rank(window, now - self.sound)


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


def rank(window, delta):
    value = window - delta
    if value <= 1:
        return 0.0
    elif value >= window:
        return 1.0
    else:
        return math.log(value, window)


def presence_rank(
    weight_sound_sensor, weight_motion_sensor, window, now, sensor_readings
):
    sound = weight_sound_sensor * sensor_readings.get_sound_rank(window, now)
    motion_1 = weight_motion_sensor * sensor_readings.get_motion_rank_1(window, now)
    motion_2 = weight_motion_sensor * sensor_readings.get_motion_rank_2(window, now)

    return sound + motion_1 + motion_2


def run(external_config, external_state):
    config = Config(**external_config)
    sensor_readings = SensorReadings(**external_state)

    sound_sensor = gpiozero.MotionSensor(config.pins.sound_sensor)
    motion_sensor_1 = gpiozero.MotionSensor(config.pins.motion_sensor_1)
    motion_sensor_2 = gpiozero.MotionSensor(config.pins.motion_sensor_2)

    sound_sensor.when_motion = lambda: sensor_readings.update_sound(generateTimestamp())

    motion_sensor_1.when_motion = lambda: sensor_readings.update_motion_1(
        generateTimestamp()
    )
    motion_sensor_2.when_motion = lambda: sensor_readings.update_motion_2(
        generateTimestamp()
    )

    max_sleep_time = 1e-9 / config.frequency

    weight_total = config.weights.motion + config.weights.sound
    weight_sound_sensor = config.weights.sound / weight_total
    weight_motion_sensor = (config.weights.motion / 2) / weight_total

    while True:
        now = generateTimestamp()
        rank = presence_rank(
            weight_sound_sensor,
            weight_motion_sensor,
            config.window,
            now,
            sensor_readings,
        )
        config.action(TriggerEvent(rank=rank, timestamp=now))
        time_elapsed = generateTimestamp() - now
        sleep_time = max_sleep_time - time_elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
