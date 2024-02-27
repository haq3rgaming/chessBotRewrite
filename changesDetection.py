import numpy as np
import cv2
from copy import deepcopy
from piecesDetection import displayVerityArray

class changesDetection:
    def __init__(self) -> None:
        self.queue = []

    def show(self) -> None:
        for i in range(len(self.queue)):
            displayVerityArray(self.queue[i], f"Image {i}, {id(self.queue[i])}")
            
    def add(self, image: np.ndarray) -> None:
        self.queue.append(deepcopy(image))
        self.show()
    
    def pop(self) -> None:
        if len(self.queue) == 0:
            print("Queue is empty")
            return False
        cv2.destroyWindow(f"Image {len(self.queue) - 1}, {id(self.queue[-1])}")
        self.queue.pop(-1)
        self.show()

    def detect(self) -> None:
        if len(self.queue) < 2:
            print("Not enough images in queue")
            return False
        else:
            changes = np.logical_xor(self.queue[-2], self.queue[-1])
            changesFrom = np.argwhere(np.logical_and(changes, self.queue[-2])).tolist()
            changesTo =  np.argwhere(np.logical_and(changes, self.queue[-1])).tolist()
            if len(changesFrom) == 0 or len(changesTo) == 0:
                print("No changes")
                print(changesFrom, "|", changesTo)
                return False
            if len(changesFrom) > 1:
                # detect castling
                if (changesFrom[0][0], changesTo[0][0]) in ((7, 7), (0, 0)):
                    # kingside
                    if (changesFrom[0][1] == 7 or changesFrom[1][1] == 7) and (changesTo[0][1] == 5 or changesTo[1][1] == 5):
                        return [[changesFrom[0][0], 4]], [[changesFrom[0][0], 6]]
                    # queenside
                    else:
                        return [[changesFrom[0][0], 4]], [[changesFrom[0][0], 2]]
                else:
                    print("Too many changes")
                    return False
            if len(changesTo) != len(changesFrom):
                print("Changes are not equal")
                return False
            return changesFrom, changesTo

if __name__ == "__main__":
    from configManager import ConfigManager
    from warp import Warp
    from camera import Camera
    from chessboard import Board
    from mask import Mask
    from piecesDetection import piecesDetection
    import positionConverter


    configManager = ConfigManager("config.json")
    config = configManager.loadConfig()

    warper = Warp(config["warpPoints"])
    masker = Mask(config["hsv"]["white"]["upper"], config["hsv"]["white"]["lower"])
    camera = Camera(config["cameraID"])
    piecesDetector = piecesDetection()
    detector = changesDetection()
    chessboard = Board()

    cv2.namedWindow("Chessboard", cv2.WINDOW_AUTOSIZE)
    
    while True:
        chessboard.display()
        key = cv2.waitKey(0)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
            case "a":
                whiteVerityArray = piecesDetector.createVerityArrayFromMask(masker.maskByColor(warper.warp(camera.photo()))).tolist()
                detector.add(whiteVerityArray)
                print("Added")
            case "r":
                detector.pop()
                print("Removed")
            case "d":
                if changes := detector.detect():
                    tileFrom = positionConverter.array2pos(changes[0][0])
                    tileTo = positionConverter.array2pos(changes[1][0])
                    print(tileFrom, "->", tileTo, end=" | ")
                    print("Legal" if chessboard.isLegalMove(tileFrom + tileTo) else "Illegal")
                else:
                    print("Detect failed")
            case "p":
                if tileFrom is None:
                    print("Need change")
                else:
                    print("Pushing", tileFrom, "->", tileTo)
                    if chessboard.isLegalMove(tileFrom + tileTo):
                        chessboard.move(tileFrom + tileTo)
                    else:
                        print("Cannot push, move is illegal")
            case "c":
                chessboard.turn(not chessboard.turn())
                print("Changes turn to:", "White" if chessboard.turn() else "Black")
            case "t":
                print("Current turn:", "White" if chessboard.turn() else "Black")
