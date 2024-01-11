import gpiozero
import logging
import math
import time
import rpi_sentry_core.api as api

logger = logging.getLogger(__name__)


def generate_timestamp():
    return time.time_ns()


def sleep_for(duration):
    if duration > 0:
        duration_in_seconds = duration / 1e9
        logger.debug("sleeping for %s seconds", duration_in_seconds)
        time.sleep(duration_in_seconds)


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
    sound = weight_sound_sensor * rank(window, now - sensor_readings.sound)
    motion_1 = weight_motion_sensor * rank(window, now - sensor_readings.motion_1)
    motion_2 = weight_motion_sensor * rank(window, now - sensor_readings.motion_2)
    total = sound + motion_1 + motion_2

    logger.debug(
        "presence rank: %s (sound) + %s (motion 1) + %s (motion 2) = %s (total)",
        sound,
        motion_1,
        motion_2,
        total,
    )

    return total


def run(external_config, external_state):
    config = api.Config(**external_config)

    logger.info("configuration: %s", config)

    sensor_readings = api.SensorReadings(**external_state)

    sound_sensor = gpiozero.MotionSensor(config.pins.sound_sensor)
    motion_sensor_1 = gpiozero.MotionSensor(config.pins.motion_sensor_1)
    motion_sensor_2 = gpiozero.MotionSensor(config.pins.motion_sensor_2)

    def update_sound():
        sensor_readings.sound = generate_timestamp()

    def update_motion_1():
        sensor_readings.motion_1 = generate_timestamp()

    def update_motion_2():
        sensor_readings.motion_2 = generate_timestamp()

    sound_sensor.when_motion = update_sound
    motion_sensor_1.when_motion = update_motion_1
    motion_sensor_2.when_motion = update_motion_2

    max_sleep_time = 1e9 / config.frequency

    weight_total = config.weights.motion + config.weights.sound
    weight_sound_sensor = config.weights.sound / weight_total
    weight_motion_sensor = (config.weights.motion / 2) / weight_total

    while True:
        now = generate_timestamp()
        rank = presence_rank(
            weight_sound_sensor,
            weight_motion_sensor,
            config.window * 1e9,
            now,
            sensor_readings,
        )
        config.action(api.TriggerEvent(rank=rank, timestamp=now))
        time_elapsed = generate_timestamp() - now
        sleep_for(max_sleep_time - time_elapsed)
