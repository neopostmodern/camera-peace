from collections import deque
from dataclasses import dataclass
from subprocess import Popen, PIPE
from os import setsid, killpg
from signal import SIGTERM
from typing import Callable, List

import cv2

from camera_detection import Camera
from config import FRAME_HISTORY_LENGTH, WIDTH, HEIGHT


class MODE:
    FREEZE = "freeze"
    STUTTER = "stutter"
    ARTIFACTS = "artifacts"
    RECORD = "record"
    LOOP = "loop"
    VIEW = "view"


@dataclass
class Mode:
    name: str
    key: str
    # on_toggle is passed the intended future active state, must return the next active state
    on_toggle: Callable[[bool], bool] = lambda x: x
    active: bool = False


class Core:
    frame_count = 0
    # todo: mostly unused - remove? or use for another artifact?
    last_frames = deque(maxlen=FRAME_HISTORY_LENGTH)
    frozen_frame = None
    recorded_frames = []
    loop_frames = []
    loop_frames_offset = None
    ffplay_process = None
    modes = {}

    available_input_cameras: List[Camera]
    input_camera: Camera
    input_video_capture: cv2.VideoCapture = None
    output_camera: Camera

    def __init__(self, input_cameras, output_camera):
        self.available_input_cameras = input_cameras
        self.output_camera = output_camera

        self.register_mode(MODE.FREEZE, "f", self.store_frozen_frame)
        self.register_mode(MODE.STUTTER, "s")
        self.register_mode(MODE.ARTIFACTS, "a")
        self.register_mode(MODE.RECORD, "r", self.manage_recorded_frames)
        self.register_mode(MODE.LOOP, "l", self.manage_loop)
        self.register_mode(MODE.VIEW, "v", self.manage_playback)

    def register_mode(self, name, key, on_toggle=lambda x: x, active=False):
        self.modes[name] = Mode(name, key, on_toggle, active)

    def store_frozen_frame(self, active):
        if active:
            self.frozen_frame = self.last_frames[-1]
        else:
            self.frozen_frame = None

        return active

    def manage_recorded_frames(self, active):
        if not active:
            self.loop_frames = self.recorded_frames
            self.recorded_frames = []

        return active

    def manage_loop(self, active):
        if active and (self.loop_frames is None or len(self.loop_frames) == 0):
            return False

        if active:
            self.loop_frames_offset = self.frame_count

        return active

    def manage_playback(self, active):
        if active:
            self.ffplay_process = Popen(
                ["/usr/bin/ffplay", self.output_camera.path],
                stdout=PIPE,
                stderr=PIPE,
                shell=False,
                preexec_fn=setsid,
            )
        else:
            killpg(self.ffplay_process.pid, SIGTERM)

        return active

    def open_input_camera(self, camera: Camera):
        if self.input_video_capture is not None:
            self.input_video_capture.release()

        self.input_video_capture = cv2.VideoCapture(
            int(camera.path.replace("/dev/video", ""))
        )
        self.input_video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.input_video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.input_camera = camera
