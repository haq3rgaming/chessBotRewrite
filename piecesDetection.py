import cv2
import numpy as np
import mask, warp, configManager, camera

def splitImage(image: np.ndarray, size: list=(8,8)) -> list[np.ndarray]:
    height, width = image.shape[:2]
    h, w = height//size[0], width//size[1]
    parts = [image[i*h:(i+1)*h, j*w:(j+1)*w] for i in range(size[0]) for j in range(size[1])]
    return np.array(parts).reshape(size[0], size[1], h, w)

def thresholdFromImage(image: np.ndarray, threshold: float=0.25) -> bool:
    return np.count_nonzero(image) / image.size > threshold

def createVerityArrayFromMask(mask: np.ndarray, threshold: float=0.25, size: list=(8,8)) -> np.ndarray:
    splitImg = splitImage(mask)
    return np.array([thresholdFromImage(splitImg[i][j], threshold) for i in range(size[0]) for j in range(size[1])]).reshape(size[0], size[1])

if __name__ == "__main__":
    config = configManager.loadConfig()
    warpPoints = config["warpPoints"]
    whiteUpper = config["hsv"]["white"]["upper"]
    whiteLower = config["hsv"]["white"]["lower"]

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Masked", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Verity Array", cv2.WINDOW_AUTOSIZE)
    
    while True:
        image = warp.warpImage(camera.photo(), warpPoints)
        cv2.imshow("Camera", warp.createLines(image))
        cv2.imshow("Masked", mask.maskByColor(image, whiteUpper, whiteLower))
        whiteVerityArray = createVerityArrayFromMask(mask.maskByColor(image, whiteUpper, whiteLower)).tolist()
        whiteVerityImage = np.zeros((8,8,3), dtype=np.uint8); whiteVerityImage[whiteVerityArray] = [255,255,255]
        cv2.imshow("White Verity Array", warp.createLines(cv2.resize(whiteVerityImage, (0,0), fx=50, fy=50, interpolation=cv2.INTER_NEAREST)))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break