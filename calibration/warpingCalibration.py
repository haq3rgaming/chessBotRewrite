import cv2

textColor = (127, 255, 127)

def mouseEvent(event, x, y, flags, param) -> None:
    global warpPoints
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(image, (x, y), 2, textColor, -1)
        match len(warpPoints):
            case 0: cv2.putText(image, "Top Left", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, textColor, 1)
            case 1: cv2.putText(image, "Top Right", (x, y), cv2.FONT_HERSHEY_PLAIN , 1, textColor, 1)
            case 2: cv2.putText(image, "Bottom Left", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, textColor, 1)
            case 3: cv2.putText(image, "Bottom Right", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, textColor, 1)
        warpPoints.append((x, y))

warpPoints = []

cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback("Camera", mouseEvent)

if __name__ == "__main__":
    from configManager import ConfigManager
    from warp import Warp
    from camera import Camera

    configManager = ConfigManager("config.json")
    config = configManager.loadConfig()

    warper = Warp(config["warpPoints"])
    camera = Camera(config["cameraID"])


    image = camera.photo()
    while True:
        cv2.imshow("Camera", image)
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
            case "r":
                print("Reset warp points")
                warpPoints = []
                image = camera.photo()
            case "s":
                print("Warp points:", warpPoints)
                configManager.config["warpPoints"] = warpPoints
                configManager.saveConfig()
            case "w":
                warper.update(warpPoints)
                if len(warpPoints) == 4:
                    print("Warping image")
                    image = warper.warp(camera.photo())
                else:
                    print("Not enough warp points")
    camera.release()
    cv2.destroyAllWindows()