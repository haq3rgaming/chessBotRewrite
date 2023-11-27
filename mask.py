import cv2
import numpy as np

def hsv2bgr(hsv: tuple[int]) -> tuple[int]:
    return tuple(cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0])

def bgr2hsv(bgr: tuple[int]) -> tuple[int]:
    return tuple(cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0])

def maskByColor(image: np.ndarray, upper: tuple[int], lower: tuple[int]) -> np.ndarray:
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.inRange(imageHSV, np.array(lower), np.array(upper))

if __name__ == "__main__":
    import camera, configManager, warp

    config = configManager.loadConfig()
    warpPoints = config["warpPoints"]
    upper = config["hsv"]["white"]["upper"]
    lower = config["hsv"]["white"]["lower"]

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Masked", cv2.WINDOW_AUTOSIZE)

    while True:
        image = warp.warpImage(camera.photo(), warpPoints)
        cv2.imshow("Camera", warp.createLines(image))
        cv2.imshow("Masked", maskByColor(image, upper, lower))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break