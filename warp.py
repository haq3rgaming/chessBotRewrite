import cv2
import numpy as np

def warpImage(image: np.ndarray, points) -> np.ndarray:
    width = image.shape[1]
    height = image.shape[0]
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(image, matrix, (width, height))

if __name__ == "__main__":
    import camera, configManager

    config = configManager.loadConfig()
    warpPoints = config["warpPoints"]

    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    while True:
        image = camera.photo()
        cv2.imshow("Camera", warpImage(image, warpPoints))
        key = cv2.waitKey(1)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
    camera.release()
    cv2.destroyAllWindows()