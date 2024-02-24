import cv2
import numpy as np
from warp import createLines

class piecesDetection:
    def __init__(self, size: list=(8,8), threshold: float=0.20) -> None:
        self.size = size
        self.threshold = threshold

    def splitImage(self, image: np.ndarray) -> list[np.ndarray]:
        height, width = image.shape[:2]
        h, w = height//self.size[0], width//self.size[1]
        parts = [image[i*h:(i+1)*h, j*w:(j+1)*w] for i in range(self.size[0]) for j in range(self.size[1])]
        return np.array(parts).reshape(self.size[0], self.size[1], h, w)

    def thresholdFromImage(self, image: np.ndarray) -> bool:
        return np.count_nonzero(image) / image.size > self.threshold

    def createVerityArrayFromMask(self, mask: np.ndarray) -> np.ndarray:
        splitImg = self.splitImage(mask)
        matrix = np.array([self.thresholdFromImage(splitImg[i][j]) for i in range(self.size[0]) for j in range(self.size[1])]).reshape(self.size[0], self.size[1])
        return np.rot90(matrix, 1)

def displayVerityArray(array, windowName, size: list=(8,8)):
    image = np.zeros((size[0], size[1], 3), dtype=np.uint8); image[array] = [255,255,255]
    cv2.imshow(windowName, createLines(cv2.resize(image, (0,0), fx=50, fy=50, interpolation=cv2.INTER_NEAREST)))

if __name__ == "__main__":
    from configManager import ConfigManager
    from warp import Warp
    from camera import Camera
    from mask import Mask

    configManager = ConfigManager("config.json")
    config = configManager.loadConfig()

    warper = Warp(config["warpPoints"])
    maskerWhite = Mask(config["hsv"]["white"]["upper"], config["hsv"]["white"]["lower"])
    maskerBlack = Mask(config["hsv"]["black"]["upper"], config["hsv"]["black"]["lower"])
    camera = Camera(config["cameraID"])
    piecesDetectWhite = piecesDetection()
    piecesDetectBlack = piecesDetection()

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("MaskedWhite", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("MaskedBlack", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("White Verity Array", cv2.WINDOW_AUTOSIZE)
    
    while True:
        image = warper.warp(camera.photo())
        cv2.imshow("Camera", createLines(image))
        cv2.imshow("MaskedWhite", maskerWhite.maskByColor(image))
        cv2.imshow("MaskedBlack", maskerBlack.maskByColor(image))
        whiteVerityArray = piecesDetectWhite.createVerityArrayFromMask(maskerWhite.maskByColor(image)).tolist()
        whiteVerityImage = np.zeros((8,8,3), dtype=np.uint8); whiteVerityImage[whiteVerityArray] = [255,255,255]
        blackVerityArray = piecesDetectBlack.createVerityArrayFromMask(maskerBlack.maskByColor(image)).tolist()
        blackVerityImage = np.zeros((8,8,3), dtype=np.uint8); blackVerityImage[blackVerityArray] = [255,255,255]
        cv2.imshow("White Verity Array", createLines(cv2.resize(whiteVerityImage, (0,0), fx=50, fy=50, interpolation=cv2.INTER_NEAREST)))
        cv2.imshow("Black Verity Array", createLines(cv2.resize(blackVerityImage, (0,0), fx=50, fy=50, interpolation=cv2.INTER_NEAREST)))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break