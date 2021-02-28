import curses

from core import MODE


class COLORS:
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4


def spinner_character(counter):
    spinner = "⠈⠐⠠⢀⡀⠄⠂⠁"
    return spinner[counter % len(spinner)]


def initialize_interface(win):
    win.nodelay(True)
    curses.cbreak()
    # curses.echo()
    curses.init_pair(COLORS.RED, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLORS.GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLORS.BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(COLORS.YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)


def render_interface(
    win, core, stutter_frame_counter, artifact_frame_counter, error=None
):
    win.clear()
    win.addstr(
        0, 0, spinner_character(core.frame_count), curses.color_pair(COLORS.GREEN),
    )
    win.addstr(0, 3, f"{core.frame_count: 6} frames")
    win.addstr(0, 20, f"Output camera: {core.output_camera.path}")

    line = 2

    if error is not None:
        win.addstr(line, 0, error, curses.color_pair(COLORS.RED))
        line += 2

    win.addstr(line, 0, "Input Camera:")
    win.addstr(line, 15, core.input_camera.name, curses.color_pair(COLORS.GREEN))
    if len(core.available_input_cameras) > 1:
        for camera_index, camera in enumerate(core.available_input_cameras):
            if camera.identifier == core.input_camera.identifier:
                continue

            line += 1
            win.addstr(
                line, 0, str(camera_index), curses.color_pair(COLORS.BLUE),
            )
            win.addstr(
                line, 3, camera.name,
            )

    line += 2
    win.addstr(
        line, 0, f"MODES",
    )
    for mode_index, mode in enumerate(core.modes.values()):
        line += 1
        win.addstr(line, 0, mode.key, curses.color_pair(COLORS.BLUE))
        win.addstr(
            line,
            3,
            "✓️" if mode.active else "✗️",
            curses.color_pair(COLORS.GREEN if mode.active else COLORS.RED),
        )
        win.addstr(line, 6, mode.name.capitalize())

        if mode.name == MODE.RECORD and len(core.recorded_frames) > 0:
            win.addstr(line, 15, f"({len(core.recorded_frames)} frames)")
        if mode.name == MODE.LOOP and len(core.loop_frames) > 0:
            if mode.active:
                frame_index = (
                    (core.frame_count - core.loop_frames_offset) % len(core.loop_frames)
                ) + 1
                win.addstr(
                    line, 15, f"(frame {frame_index: 3} of {len(core.loop_frames)})"
                )
            else:
                win.addstr(line, 15, f"({len(core.loop_frames)} frames available)")

    line += 1
    for counter_index, (mode, counter) in enumerate(
        (
            {
                MODE.STUTTER: stutter_frame_counter,
                MODE.ARTIFACTS: artifact_frame_counter,
            }
        ).items()
    ):
        line += 1
        color = COLORS.RED
        if core.modes[mode].active:
            color = COLORS.YELLOW
        if counter > 0:
            color = COLORS.GREEN

        win.addstr(
            line, 0, "●" if counter > 0 else "○", curses.color_pair(color),
        )
        win.addstr(line, 3, mode.capitalize())
        if counter > 0:
            win.addstr(line, 14, f"({str(counter)} frames remaining)")

    line += 2
    win.addstr(line, 0, "q", curses.color_pair(COLORS.BLUE))
    win.addstr(line, 3, "Quit")
