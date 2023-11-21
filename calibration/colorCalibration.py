import cv2
import numpy as np
import camera, warp, configManager, mask

textColor = (127, 255, 127)
distance = 20

def sliderChange(value) -> None:
    global trackbarSetup, upper, lower
    if not trackbarSetup: return
    lower = cv2.getTrackbarPos("HueMin", "HSV Sliders White"), cv2.getTrackbarPos("SatMin", "HSV Sliders White"), cv2.getTrackbarPos("ValMin", "HSV Sliders White")
    upper = cv2.getTrackbarPos("HueMax", "HSV Sliders White"), cv2.getTrackbarPos("SatMax", "HSV Sliders White"), cv2.getTrackbarPos("ValMax", "HSV Sliders White")

def mouseEvent(event, x, y, flags, param) -> None:
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = mask.bgr2hsv(image[y][x])
        cv2.setTrackbarPos("HueMin", "HSV Sliders White", pixel[0] - distance)
        cv2.setTrackbarPos("SatMin", "HSV Sliders White", pixel[1] - distance)
        cv2.setTrackbarPos("ValMin", "HSV Sliders White", pixel[2] - distance)
        cv2.setTrackbarPos("HueMax", "HSV Sliders White", pixel[0] + distance)
        cv2.setTrackbarPos("SatMax", "HSV Sliders White", pixel[1] + distance)
        cv2.setTrackbarPos("ValMax", "HSV Sliders White", pixel[2] + distance)

if __name__ == "__main__":
    config = configManager.loadConfig()
    warpPoints = config["warpPoints"]
    upper = config["hsv"]["upper"]
    lower = config["hsv"]["lower"]
    
    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Masked", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("HSV Sliders White", cv2.WINDOW_AUTOSIZE)

    trackbarSetup = False
    cv2.createTrackbar("HueMin", "HSV Sliders White", lower[0], 255, sliderChange)
    cv2.createTrackbar("SatMin", "HSV Sliders White", lower[1], 255, sliderChange)
    cv2.createTrackbar("ValMin", "HSV Sliders White", lower[2], 255, sliderChange)
    cv2.createTrackbar("HueMax", "HSV Sliders White", upper[0], 255, sliderChange)
    cv2.createTrackbar("SatMax", "HSV Sliders White", upper[1], 255, sliderChange)
    cv2.createTrackbar("ValMax", "HSV Sliders White", upper[2], 255, sliderChange)
    trackbarSetup = True

    cv2.setMouseCallback("Camera", mouseEvent)

    while True:
        image = warp.warpImage(camera.photo(), warpPoints)
        cv2.imshow("Camera", image)
        cv2.imshow("Masked", cv2.bitwise_and(image, image, mask=mask.maskByColor(image, upper, lower)))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
            case "s":
                print("Saving config")
                config["hsv"]["upper"] = upper
                config["hsv"]["lower"] = lower
                configManager.saveConfig(config)
    camera.release()
    cv2.destroyAllWindows()