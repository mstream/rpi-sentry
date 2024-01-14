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
sensor_size = (2304, 1296)
output_size = (1492, sensor_size[1])
horizontal_crop = sensor_size[0] - output_size[0]
frames_per_second = 10
bitrate = 5000000

frame_duration = round(1000000 / frames_per_second)

video_config = picam2.create_video_configuration(
    buffer_count=buffer_count,
    controls={
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
