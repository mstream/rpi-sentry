import rpi_sentry_core.trigger as trigger
import pydantic as p
import typing


class Camera:
    def shoot(self, rank: float, path: trigger.CaptureFilePath) -> None:
        pass


class SensorReadings(p.BaseModel):
    motion_1: float
    motion_2: float
    sound: float


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
