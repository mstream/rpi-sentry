import cv2
import enum
import libcamera
from encoder import H264Encoder
from picamera2 import Picamera2
from picamera2.outputs import CircularOutput
import storage
import time

Mode = enum.Enum("CameraMode", ["ALWAYS_ON", "AUTOMATIC"])
State = enum.Enum("State", ["IDLING", "MOTION_SENSING", "RECORDING"])


def imx708_parameters():
    return {
        "af_window_factor": 3,
        "buffer_count": 15,
        "circular_buffer_length_in_seconds": 5,
        "frames_per_second": 15,
        "preview_size_factor": 4,
        "real_sensor_size": (4608, 2592),
        "sensor_size_factor": 2,
    }


def ov64a40_parameters():
    return {
        "af_window_factor": 3,
        "buffer_count": 18,
        "circular_buffer_length_in_seconds": 5,
        "frames_per_second": 12,
        "preview_size_factor": 4,
        "real_sensor_size": (9248, 6944),
        "sensor_size_factor": 4,
    }


parameters = ov64a40_parameters()


class Camera:
    def __init__(self, root_dir_path):
        self.trigger_threshold = 0.5
        self.maximum_recording_length = 30
        self.prev_frame = None
        self.recording_start_time = 0
        self.root_dir_path = root_dir_path
        self.mode = Mode.AUTOMATIC
        self.state = State.IDLING
        self.initialize_picam2(**parameters)

    def initialize_picam2(
        self,
        af_window_factor,
        buffer_count,
        circular_buffer_length_in_seconds,
        frames_per_second,
        preview_size_factor,
        real_sensor_size,
        sensor_size_factor,
    ):
        af_window_size = (
            round(real_sensor_size[0] / (1.0 * af_window_factor)),
            round(real_sensor_size[1] / af_window_factor),
        )

        scaled_sensor_size = (
            round(real_sensor_size[0] / sensor_size_factor),
            round(real_sensor_size[1] / sensor_size_factor),
        )

        w = scaled_sensor_size[0]
        h = scaled_sensor_size[1]

        # H264 4.0 limit
        pixels_limit = 256 * 8144

        while w * h > pixels_limit or w != h:
            if h > w:
                h -= 4
            else:
                w -= 4

        cropped_real_sensor_size = (w * sensor_size_factor, h * sensor_size_factor)

        crop_margin_size = (
            real_sensor_size[0] - cropped_real_sensor_size[0],
            real_sensor_size[1] - cropped_real_sensor_size[1],
        )

        output_size = (
            round(cropped_real_sensor_size[0] / sensor_size_factor),
            round(cropped_real_sensor_size[1] / sensor_size_factor),
        )

        preview_size = (
            round(output_size[0] / preview_size_factor),
            round(output_size[1] / preview_size_factor),
        )

        frame_duration = round(1000000 / frames_per_second)

        self.motion_detection_frame_duration_limits = (
            round(frame_duration / 12),
            round(frame_duration / 12),
        )

        self.recording_frame_duration_limits = (frame_duration, frame_duration)

        picam2 = Picamera2()

        video_config = picam2.create_video_configuration(
            buffer_count=buffer_count,
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
                "FrameDurationLimits": self.motion_detection_frame_duration_limits,
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

        print(f"Video config: {video_config}")

        picam2.configure(video_config)

        encoder = H264Encoder(
            framerate=frames_per_second,
            height=output_size[1],
            width=output_size[0],
        )

        circular_output = CircularOutput(
            buffersize=circular_buffer_length_in_seconds * frames_per_second,
            file=None,
        )

        encoder.output = circular_output

        self.countour_area_threshold = preview_size[0] * preview_size[1] * 0.005
        self.encoder = encoder
        self.picam2 = picam2

    @property
    def preview_image(self):
        if self.prev_frame is not None:
            _, jpeg = cv2.imencode(".jpg", self.prev_frame)
            return jpeg.tobytes()
        else:
            return None

    def is_motion_detected(self, next_frame_arr):
        next_frame = cv2.cvtColor(next_frame_arr, cv2.COLOR_YUV420P2GRAY)
        result = False
        if self.prev_frame is not None:
            diff = cv2.absdiff(self.prev_frame, next_frame)
            blur = cv2.GaussianBlur(diff, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(
                dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )
            for contour in contours:
                if cv2.contourArea(contour) >= self.countour_area_threshold:
                    result = True
                    break
        self.prev_frame = next_frame
        return result

    def update(self):
        match self.state:
            case State.IDLING:
                self.update_idling(rank=1.0)
            case State.MOTION_SENSING:
                self.update_motion_sensing(rank=1.0, timestamp=0)
            case State.RECORDING:
                self.update_recording(rank=1.0)

    def update_idling(self, rank):
        if self.rank_is_above_trigger(rank):
            self.picam2.start()
            self.picam2.start_encoder(self.encoder)
            self.start_motion_sensing()

    def update_motion_sensing(self, rank, timestamp):
        if self.rank_is_below_trigger(rank):
            self.picam2.stop_encoder()
            self.picam2.stop()
            self.state = State.IDLING
        else:
            if self.is_motion_detected(self.picam2.capture_array("lores")):
                file_output = storage.prepare_file_path(
                    rank=1.0,
                    root_dir_path=self.root_dir_path,
                    timestamp=timestamp,
                )
                self.encoder.output.fileoutput = file_output
                print(f"saving footage to {file_output} ...")
                self.encoder.output.start()
                self.recording_start_time = time.time()
                self.state = State.RECORDING
                self.picam2.set_controls(
                    {"FrameDurationLimits": self.recording_frame_duration_limits}
                )

    def update_recording(self, rank):
        if self.should_stop_recording(rank):
            self.encoder.output.stop()
            self.start_motion_sensing()
            print("... done")

    def start_motion_sensing(self):
        self.prev_frame = None
        self.state = State.MOTION_SENSING
        self.picam2.set_controls(
            {"FrameDurationLimits": self.motion_detection_frame_duration_limits}
        )

    def should_stop_recording(self, rank):
        if self.is_motion_detected(self.picam2.capture_array("lores")):
            return False

        recording_length_reached = (
            time.time() - self.recording_start_time >= self.maximum_recording_length
        )
        return self.state == State.RECORDING and (
            recording_length_reached or self.rank_is_below_trigger(rank)
        )

    def rank_is_below_trigger(self, rank):
        return rank < self.trigger_threshold

    def rank_is_above_trigger(self, rank):
        return rank >= self.trigger_threshold
