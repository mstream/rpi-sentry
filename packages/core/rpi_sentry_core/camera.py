import libcamera
import logging
import os
from pathlib import Path
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
import rpi_sentry_core.api as api
import time

logger = logging.getLogger(__name__)

picam2 = Picamera2()

buffer_count = 10
sensor_size_factor = 2
af_window_factor = 3
frames_per_second = 10

real_sensor_size = (4608, 2592)

sensor_size = (
    round(real_sensor_size[0] / sensor_size_factor),
    round(real_sensor_size[1] / sensor_size_factor),
)

output_size = (sensor_size[0] - 812, sensor_size[1])
horizontal_crop = sensor_size[0] - output_size[0]
af_window_size = (
    round(real_sensor_size[0] / af_window_factor),
    round(real_sensor_size[1] / af_window_factor),
)

frame_duration = round(1000000 / frames_per_second)

video_config = picam2.create_video_configuration(
    buffer_count=buffer_count,
    controls={
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
            round(horizontal_crop / 2),
            0,
            sensor_size[0] - horizontal_crop,
            sensor_size[1],
        ),
    },
    display=None,
    encode="main",
    lores=None,
    main={"format": "YUV420", "size": output_size},
    queue=True,
    sensor={"bit_depth": 10, "output_size": output_size},
)

picam2.configure(video_config)


encoder = H264Encoder(bitrate=None, repeat=False, iperiod=None)


class RealCamera(api.Camera):
    def __init__(self, root_dir_path):
        self.root_dir_path = root_dir_path
        logger.debug("camera properties %s", picam2.camera_properties)
        logger.debug("camera configuration %s", picam2.camera_configuration())

    def shoot(self, rank, path):
        dir_path = os.path.join(self.root_dir_path, path.dir_name)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(dir_path, f"{path.file_base_name}.h264")
        print("real camera shoot at rank ", rank)
        picam2.start_recording(encoder, file_path, quality=Quality.VERY_HIGH)
        print("recording...")
        time.sleep(10)
        picam2.stop_recording()
        print("saving to", file_path)
