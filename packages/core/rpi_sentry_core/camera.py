from enum import Enum
import libcamera
import logging
import numpy as np
import os
from pathlib import Path
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import CircularOutput, FileOutput
import pydantic as p
import rpi_sentry_core.api as api
import time

logger = logging.getLogger(__name__)


class Params(p.BaseModel):
    af_window_factor: p.PositiveInt
    buffer_count: p.PositiveInt
    circular_buffer_length_in_seconds: p.PositiveInt
    frames_per_second: p.PositiveInt
    preview_size_factor: p.PositiveInt
    sensor_size_factor: p.PositiveInt


State = Enum("State", ["IDLE", "MOTION_SENSING", "RECORDING"])


class RealCamera(api.Camera):
    def __init__(self, root_dir_path):
        self.prev = None
        self.recording_start_time = np.nan
        self.root_dir_path = root_dir_path
        self.state = State.IDLE
        self.trigger_threshold = 0.5
        self.initialize_picam2(
            {
                "af_window_factor": 3,
                "buffer_count": 15,
                "circular_buffer_length_in_seconds": 3,
                "frames_per_second": 15,
                "preview_size_factor": 4,
                "sensor_size_factor": 2,
            }
        )

    def initialize_picam2(self, external_params):
        params = Params(**external_params)
        picam2 = Picamera2()

        real_sensor_size = (4608, 2592)

        af_window_size = (
            round(real_sensor_size[0] / (1.0 * params.af_window_factor)),
            round(real_sensor_size[1] / params.af_window_factor),
        )

        cropped_real_sensor_size = (real_sensor_size[0] - 1624, real_sensor_size[1])

        crop_margin_size = (
            real_sensor_size[0] - cropped_real_sensor_size[0],
            real_sensor_size[1] - cropped_real_sensor_size[1],
        )

        scaled_sensor_size = (
            round(real_sensor_size[0] / params.sensor_size_factor),
            round(real_sensor_size[1] / params.sensor_size_factor),
        )

        output_size = (
            round(cropped_real_sensor_size[0] / params.sensor_size_factor),
            round(cropped_real_sensor_size[1] / params.sensor_size_factor),
        )

        preview_size = (
            round(output_size[0] / params.preview_size_factor),
            round(output_size[1] / params.preview_size_factor),
        )

        frame_duration = round(1000000 / params.frames_per_second)

        video_config = picam2.create_video_configuration(
            buffer_count=params.buffer_count,
            controls={
                "AfMetering": libcamera.controls.AfMeteringEnum.Windows,
                "AfMode": libcamera.controls.AfModeEnum.Continuous,
                "AfWindows": [
                    (
                        round(af_window_size[0] / 2),
                        round(af_window_size[1] / 2),
                        real_sensor_size[0] - af_window_size[0],
                        real_sensor_size[1] - af_window_size[1],
                    )
                ],
                "AwbEnable": True,
                "AwbMode": libcamera.controls.AwbModeEnum.Auto,
                "AfRange": libcamera.controls.AfRangeEnum.Normal,
                "AfSpeed": libcamera.controls.AfSpeedEnum.Fast,
                "FrameDurationLimits": (frame_duration, frame_duration),
                "NoiseReductionMode": libcamera.controls.draft.NoiseReductionModeEnum.Off,
                "ScalerCrop": (
                    round(crop_margin_size[0] / 2),
                    round(crop_margin_size[1] / 2),
                    cropped_real_sensor_size[0],
                    cropped_real_sensor_size[1],
                ),
            },
            display=None,
            encode="main",
            lores={"format": "YUV420", "size": preview_size},
            main={"format": "YUV420", "size": output_size},
            queue=True,
            sensor={"bit_depth": 10, "output_size": scaled_sensor_size},
        )

        picam2.configure(video_config)
        logger.debug("camera properties %s", picam2.camera_properties)
        logger.debug("camera configuration %s", picam2.camera_configuration())
        encoder = H264Encoder(bitrate=None, repeat=True, iperiod=None)

        circular_output = CircularOutput(
            buffersize=params.circular_buffer_length_in_seconds
            * params.frames_per_second,
            file=None,
        )

        encoder.output = circular_output

        def capture_preview_buffer():
            w, h = preview_size
            buf = picam2.capture_buffer("lores")
            return buf[: w * h].reshape(h, w)

        self.picam2 = picam2
        self.capture_preview_buffer = capture_preview_buffer
        self.encoder = encoder

    def prepare_file_path(self, path):
        dir_path = os.path.join(self.root_dir_path, path.dir_name)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return os.path.join(dir_path, f"{path.file_base_name}.h264")

    def update(self, rank, path):
        match self.state:
            case State.IDLE:
                self.update_idle(rank, path)
            case State.MOTION_SENSING:
                self.update_motion_sensing(rank, path)
            case State.RECORDING:
                self.update_recording(rank, path)

    def update_idle(self, rank, path):
        logger.debug("CAMERA IS IDLE")
        if rank >= self.trigger_threshold:
            self.picam2.start()
            self.picam2.start_encoder(self.encoder, quality=Quality.VERY_HIGH)
            self.start_motion_sensing()

    def update_motion_sensing(self, rank, path):
        logger.debug("CAMERA IS MOTION SENSING")
        if rank < self.trigger_threshold:
            self.picam2.stop_encoder()
            self.picam2.stop()
            self.state = State.IDLE
        else:
            cur = self.capture_preview_buffer()
            if self.prev is not None:
                mse = np.square(np.subtract(cur, self.prev)).mean()
                if mse > 7:
                    self.prev = None
                    file_output = self.prepare_file_path(path)
                    self.encoder.output.fileoutput = file_output
                    logger.info("saving footage to %s", file_output)
                    self.encoder.output.start()
                    self.recording_start_time = time.time()
                    self.state = State.RECORDING
            self.prev = cur

    def update_recording(self, rank, path):
        logger.debug("CAMERA IS RECORDING")
        if time.time() - self.recording_start_time > 10.0:
            self.encoder.output.stop()
            self.start_motion_sensing()

    def start_motion_sensing(self):
        self.prev = None
        self.state = State.MOTION_SENSING
