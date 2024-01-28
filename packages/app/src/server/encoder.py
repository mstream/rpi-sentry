from v4l2 import (
    V4L2_CID_MPEG_VIDEO_H264_I_PERIOD,
    V4L2_CID_MPEG_VIDEO_H264_LEVEL,
    V4L2_CID_MPEG_VIDEO_REPEAT_SEQ_HEADER,
    V4L2_MPEG_VIDEO_H264_LEVEL_4_1,
    V4L2_PIX_FMT_H264,
)

from picamera2.encoders.v4l2_encoder import V4L2Encoder


class H264Encoder(V4L2Encoder):
    def __init__(
        self,
        framerate=30,
        height=1080,
        width=1920,
    ):
        super().__init__(10 * width * height * framerate, V4L2_PIX_FMT_H264)
        self.iperiod = None
        self.repeat = True
        self.qp = None
        self.framerate = framerate
        self._enable_framerate = True
        self._controls = []

        if self.iperiod is not None:
            self._controls += [(V4L2_CID_MPEG_VIDEO_H264_I_PERIOD, self.iperiod)]

        if self.repeat:
            self._controls += [(V4L2_CID_MPEG_VIDEO_REPEAT_SEQ_HEADER, 1)]

        self._controls += [
            (V4L2_CID_MPEG_VIDEO_H264_LEVEL, V4L2_MPEG_VIDEO_H264_LEVEL_4_1)
        ]
