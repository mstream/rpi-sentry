import rpi_sentry_core.trigger as trigger
import pydantic as p
import typing


class Camera:
    def update(self, rank: float, path: trigger.CaptureFilePath) -> None:
        pass


class SensorReadings(p.BaseModel):
    motion_1: p.StrictFloat
    motion_2: p.StrictFloat
    sound: p.StrictFloat


class TriggerEvent(p.BaseModel):
    rank: p.StrictFloat
    timestamp: p.StrictInt


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
