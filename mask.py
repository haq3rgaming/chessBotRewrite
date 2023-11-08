import cv2
import numpy as np
import warp

def hsv2bgr(hsv) -> tuple:
    return tuple(cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0])

def bgr2hsv(bgr) -> tuple:
    return tuple(cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0])

def maskByColor(image, upper, lower) -> np.ndarray:
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.inRange(imageHSV, np.array(lower), np.array(upper))

if __name__ == "__main__":
    import camera, configManager

    config = configManager.loadConfig()
    warpPoints = config["warpPoints"]
    upper = config["hsv"]["upper"]
    lower = config["hsv"]["lower"]

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Masked", cv2.WINDOW_AUTOSIZE)

    while True:
        image = warp.warpImage(camera.photo(), warpPoints)
        cv2.imshow("Camera", image)
        cv2.imshow("Masked", maskByColor(image, upper, lower))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
        