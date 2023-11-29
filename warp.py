import cv2
import numpy as np

class Warp:
    def __init__(self, points: tuple[int]) -> None:
        self.points = points

    def update(self, points: tuple[int]) -> None:
        self.points = points

    def warp(self, image: np.ndarray) -> np.ndarray:
        width = image.shape[1]
        height = image.shape[0]
        pts1 = np.float32(self.points)
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(image, matrix, (width, height))

def createLines(picture: np.ndarray, lineCount: tuple[int]=(8, 8), lineColor: tuple[int]=(255, 0, 0), lineWidth: int=2) -> np.ndarray:
    height, width = picture.shape[:2]
    linedPicture = picture.copy()
    [cv2.line(linedPicture, (0, height * i // lineCount[0]), (width, height * i // lineCount[0]), lineColor, lineWidth) for i in range(lineCount[0])]
    [cv2.line(linedPicture, (width * i // lineCount[1], 0), (width * i // lineCount[1], height), lineColor, lineWidth) for i in range(lineCount[1])]
    return linedPicture

if __name__ == "__main__":
    from configManager import ConfigManager
    from camera import Camera

    configManager = ConfigManager("config.json")
    config = configManager.loadConfig()
    
    warper = Warp(config["warpPoints"])
    camera = Camera(config["cameraID"])

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    while True:
        image = camera.photo()
        cv2.imshow("Camera", createLines(warper.warp(image)))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
    camera.release()
    cv2.destroyAllWindows()