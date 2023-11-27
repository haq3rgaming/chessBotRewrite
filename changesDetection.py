import cv2
import numpy as np
from copy import deepcopy

import mask, warp, configManager, camera, piecesDetection, positionConverter, chessboard

def detectChanges(before: list, after: list) -> list:
    changes = np.logical_xor(before, after)
    changesFrom = np.argwhere(np.logical_and(changes, before)).tolist()
    changesTo =  np.argwhere(np.logical_and(changes, after)).tolist()
    return changesFrom, changesTo

if __name__ == "__main__":
    config = configManager.loadConfig()
    warpPoints = config["warpPoints"]
    whiteUpper = config["hsv"]["white"]["upper"]
    whiteLower = config["hsv"]["white"]["lower"]

    tileFrom, tileTo, before = None, None, None

    cv2.namedWindow("Chessboard", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Before", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("After", cv2.WINDOW_AUTOSIZE)
    while True:
        chessboard.display()
        key = cv2.waitKey(0)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
            case "s":
                whiteVerityArray = piecesDetection.createVerityArrayFromMask(mask.maskByColor(warp.warpImage(camera.photo(), warpPoints), whiteUpper, whiteLower)).tolist()
                before = deepcopy(whiteVerityArray)
                piecesDetection.displayVerityArray(before, "Before")
                print("Set before")
            case "d":
                if before is None:
                    print("Set before first")
                else:
                    after = piecesDetection.createVerityArrayFromMask(mask.maskByColor(warp.warpImage(camera.photo(), warpPoints), whiteUpper, whiteLower)).tolist()
                    piecesDetection.displayVerityArray(after, "After")
                    changes = detectChanges(before, after)
                    if len(changes[0]) == 0:
                        print("No changes")
                        tileFrom, tileTo = None, None
                    elif len(changes[0]) == 1:
                        tileFrom = positionConverter.array2pos(changes[0][0])
                        tileTo = positionConverter.array2pos(changes[1][0])
                        print(tileFrom, "->", tileTo, end=" | ")
                        print("Legal" if chessboard.isLegalMove(tileFrom + tileTo) else "Illegal")
                    else:
                        print("Multiple changes", changes)
                        tileFrom, tileTo = None, None
            case "p":
                if tileFrom is None:
                    print("Need change")
                else:
                    if chessboard.isLegalMove(tileFrom + tileTo):
                        chessboard.move(tileFrom + tileTo)
                    else:
                        print("Cannot push, move is illegal")
            case "c":
                chessboard.turn(not chessboard.turn())
                print("Turn:", "White" if chessboard.turn() else "Black")
            case "t":
                print("Turn:", "White" if chessboard.turn() else "Black")
