import cv2
import numpy as np
import warp

def hsv2bgr(hsv: tuple[int]) -> tuple[int]:
        return tuple(cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0])

def bgr2hsv(bgr: tuple[int]) -> tuple[int]:
    return tuple(cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0])

class Mask:
    def __init__(self, upper: tuple[int], lower: tuple[int]) -> None:
        self.upper = upper
        self.lower = lower

    def maskByColor(self, image: np.ndarray) -> np.ndarray:
        imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return cv2.inRange(imageHSV, np.array(self.lower), np.array(self.upper))

if __name__ == "__main__":
    import camera, configManager

    configManager = ConfigManager("config.json")
    config = configManager.loadConfig()
    warper = Warp(config["warpPoints"])
    camera = Camera(config["cameraID"])
    masker = Mask(config["hsv"]["white"]["upper"], config["hsv"]["white"]["lower"])

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Masked", cv2.WINDOW_AUTOSIZE)

    while True:
        image = warper.warp(camera.photo())
        cv2.imshow("Camera", createLines(image))
        cv2.imshow("Masked", masker.maskByColor(image))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break