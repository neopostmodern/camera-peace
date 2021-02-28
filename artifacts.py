import cv2
import numpy as np

from config import WIDTH, HEIGHT


def compression_artifact(current_frame, base_frame, resize_factor=0.2):
    # generate a 'compressed' looking version (of the historical frame)
    resized_frame = cv2.resize(base_frame, None, fx=resize_factor, fy=resize_factor)
    _, resized_compressed_frame_encoded = cv2.imencode(
        ".jpg", resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 10]
    )
    resized_compressed_frame = cv2.imdecode(resized_compressed_frame_encoded, 1)
    compressed_frame = cv2.resize(resized_compressed_frame, (WIDTH, HEIGHT))

    # generate a mask
    diff = cv2.absdiff(compressed_frame, current_frame)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    threshold_mask = mask < 10

    # add the masked portion of the 'compressed' (historical) frame to the current one
    frame_composition = np.copy(current_frame)
    frame_composition[threshold_mask] = compressed_frame[threshold_mask]
    return frame_composition
