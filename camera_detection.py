from dataclasses import dataclass
from subprocess import run, PIPE


@dataclass
class Camera:
    name: str
    path: str
    identifier: str


def detect_cameras():
    v4l2_query = run(["v4l2-ctl", "--list-devices"], stdout=PIPE)
    if v4l2_query.returncode != 0:
        raise Exception("Failed to query video devices")

    v4l2_output = v4l2_query.stdout.decode()
    cameras = v4l2_output.strip().split("\n\n")

    input_cameras = []
    output_camera = None

    for camera in cameras:
        segments = [s.strip() for s in camera.split("\n")]

        name = segments[0]
        name_split_position = name.rfind("(")
        identifier = name[name_split_position:].strip("():")
        name_segments = name[:name_split_position].split(":")
        readable_name = name_segments[0]

        paths = segments[1:]
        path = paths[0]  # ignore all but the first file path offered

        if name.startswith("Dummy"):
            output_camera = Camera(readable_name, path, identifier)
        elif path.startswith("/dev/video"):
            input_cameras.append(Camera(readable_name, path, identifier))

    return input_cameras, output_camera
