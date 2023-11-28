import cv2, time
import numpy as np

class Camera:
    def __init__(self, cameraID: int) -> None:
        self.cameraID = cameraID
        self.camera = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
        time.sleep(1) # Wait for camera to start
        assert self.camera.isOpened(), "Cannot capture source"
    
    def photo(self) -> np.ndarray:
        self.camera.read() # Discard first frame for updated image
        return self.camera.read()[1]

    def release(self) -> None:
        self.camera.release()
        cv2.destroyAllWindows()