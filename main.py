from random import random, randint
import curses
from time import sleep

import cv2
import pyfakewebcam

from artifacts import compression_artifact
from camera_detection import detect_cameras
from config import (
    WIDTH,
    HEIGHT,
    FRAME_HISTORY_LENGTH,
    STUTTER_PROBABILITY,
    ARTIFACT_PROBABILITY,
    MAX_FRAMES_PER_SECOND,
)
from interface import render_interface, initialize_interface
from core import Core, MODE

input_cameras, output_camera = detect_cameras()
if len(input_cameras) == 0:
    raise Exception("No webcams to read found")
if output_camera is None:
    raise Exception("No dummy webcam to write to found; have you loaded v4l2loopback?")
core = Core(input_cameras, output_camera)
core.open_input_camera(core.available_input_cameras[0])
webcam_output = pyfakewebcam.FakeWebcam(core.output_camera.path, WIDTH, HEIGHT)


def verbose_error_handler(status, func_name, err_msg, file_name, line):
    print("Status = %d" % status)
    print("Function = %s" % func_name)
    print("Message = %s" % err_msg)
    print("Location = %s(%d)" % (file_name, line))


# cv2.redirectError(verbose_error_handler)


def pipe_webcam(win):
    stutter_frame_counter = 0
    stutter_frame = None
    artifact_frame_counter = 0
    artifact_frame = None

    initialize_interface(win)

    while True:
        error = None
        frame_read_success, frame = core.input_video_capture.read()
        if not frame_read_success:
            error = "Couldn't open camera - is it being used by another program?"

        render_interface(
            win, core, stutter_frame_counter, artifact_frame_counter, error
        )

        key = win.getch()
        if key != curses.ERR:
            if key == ord("q"):
                break

            for mode in core.modes.values():
                if key == ord(mode.key):
                    mode.active = mode.on_toggle(not mode.active)

            try:
                selected_camera = core.available_input_cameras[int(chr(key))]
                core.open_input_camera(selected_camera)
            except (ValueError, IndexError):
                pass

        if error is not None:
            sleep(1)
            continue

        # convert to correct color space
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # color corrections
        frame[:, :, 2] = frame[:, :, 2] * 0.8
        frame_to_display = frame

        if core.modes[MODE.LOOP].active:
            frame_to_display = core.loop_frames[
                (core.frame_count - core.loop_frames_offset) % len(core.loop_frames)
            ]

        if stutter_frame_counter == 0 and core.modes[MODE.ARTIFACTS].active:
            if artifact_frame_counter > 0:
                artifact_frame_counter -= 1
                frame_to_display = compression_artifact(
                    frame_to_display, artifact_frame
                )
            elif random() < ARTIFACT_PROBABILITY:
                artifact_frame_counter = randint(5, 30)
                artifact_frame = frame_to_display

        if core.modes[MODE.STUTTER].active:
            if stutter_frame_counter > 0:
                frame_to_display = stutter_frame
                stutter_frame_counter -= 1
            elif random() < STUTTER_PROBABILITY:
                stutter_frame_counter = randint(10, FRAME_HISTORY_LENGTH - 1)
                stutter_frame = frame_to_display

        if core.modes[MODE.FREEZE].active:
            frame_to_display = core.frozen_frame

        webcam_output.schedule_frame(frame_to_display)

        sleep(1 / MAX_FRAMES_PER_SECOND)
        core.frame_count += 1
        core.last_frames.append(frame_to_display)

        if core.modes[MODE.RECORD].active:
            core.recorded_frames.append(frame)


curses.wrapper(pipe_webcam)
