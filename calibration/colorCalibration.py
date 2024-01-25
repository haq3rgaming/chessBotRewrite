import cv2

distance = 20

def sliderChange(value) -> None:
    global trackbarSetup
    if not trackbarSetup: return
    configManager.config["hsv"]["black"]["lower"] = cv2.getTrackbarPos("HueMin", "HSV Sliders White"), cv2.getTrackbarPos("SatMin", "HSV Sliders White"), cv2.getTrackbarPos("ValMin", "HSV Sliders White")
    configManager.config["hsv"]["black"]["upper"] = cv2.getTrackbarPos("HueMax", "HSV Sliders White"), cv2.getTrackbarPos("SatMax", "HSV Sliders White"), cv2.getTrackbarPos("ValMax", "HSV Sliders White")
    masker.update(configManager.config["hsv"]["black"]["upper"], configManager.config["hsv"]["black"]["lower"])

def mouseEvent(event, x, y, flags, param) -> None:
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = bgr2hsv(image[y][x])
        cv2.setTrackbarPos("HueMin", "HSV Sliders White", pixel[0] - distance)
        cv2.setTrackbarPos("SatMin", "HSV Sliders White", pixel[1] - distance)
        cv2.setTrackbarPos("ValMin", "HSV Sliders White", pixel[2] - distance)
        cv2.setTrackbarPos("HueMax", "HSV Sliders White", pixel[0] + distance)
        cv2.setTrackbarPos("SatMax", "HSV Sliders White", pixel[1] + distance)
        cv2.setTrackbarPos("ValMax", "HSV Sliders White", pixel[2] + distance)

if __name__ == "__main__":
    from configManager import ConfigManager
    from warp import Warp
    from camera import Camera
    from mask import Mask, bgr2hsv

    configManager = ConfigManager("config.json")
    config = configManager.loadConfig()

    warper = Warp(config["warpPoints"])
    camera = Camera(config["cameraID"])
    masker = Mask(config["hsv"]["white"]["upper"], config["hsv"]["white"]["lower"])
    
    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Masked", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("HSV Sliders White", cv2.WINDOW_AUTOSIZE)

    trackbarSetup = False
    cv2.createTrackbar("HueMin", "HSV Sliders White", config["hsv"]["white"]["lower"][0], 255, sliderChange)
    cv2.createTrackbar("SatMin", "HSV Sliders White", config["hsv"]["white"]["lower"][1], 255, sliderChange)
    cv2.createTrackbar("ValMin", "HSV Sliders White", config["hsv"]["white"]["lower"][2], 255, sliderChange)
    cv2.createTrackbar("HueMax", "HSV Sliders White", config["hsv"]["white"]["upper"][0], 255, sliderChange)
    cv2.createTrackbar("SatMax", "HSV Sliders White", config["hsv"]["white"]["upper"][1], 255, sliderChange)
    cv2.createTrackbar("ValMax", "HSV Sliders White", config["hsv"]["white"]["upper"][2], 255, sliderChange)
    trackbarSetup = True

    cv2.setMouseCallback("Camera", mouseEvent)

    while True:
        image = warper.warp(camera.photo())
        cv2.imshow("Camera", image)
        cv2.imshow("Masked", cv2.bitwise_and(image, image, mask=masker.maskByColor(image)))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
            case "s":
                print("Saving config")
                configManager.saveConfig()
    camera.release()
    cv2.destroyAllWindows()