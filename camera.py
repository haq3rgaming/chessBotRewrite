import cv2, time
import numpy as np
from typing import Union

cameraID = 0

camera = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW); time.sleep(1)
assert camera.isOpened(), "Cannot capture source"

def photo() -> np.ndarray:
    camera.read() # Discard first frame for updated image
    return camera.read()[1]

def release() -> None:
    camera.release()
    cv2.destroyAllWindows()