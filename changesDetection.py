import cv2
import numpy as np
from copy import deepcopy

import mask, warp, configManager, camera, piecesDetection, positionConverter

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

    while True:
        image = warp.warpImage(camera.photo(), warpPoints)
        cv2.imshow("Camera", warp.createLines(image))
        cv2.imshow("Masked", mask.maskByColor(image, whiteUpper, whiteLower))
        whiteVerityArray = piecesDetection.createVerityArrayFromMask(mask.maskByColor(image, whiteUpper, whiteLower)).tolist()
        key = cv2.waitKey(0)
        if key == -1: continue
        match chr(key):
            case "q":
                print("Quit")
                break
            case " ":
                before = deepcopy(whiteVerityArray)
                after = piecesDetection.createVerityArrayFromMask(mask.maskByColor(warp.warpImage(camera.photo(), warpPoints), whiteUpper, whiteLower)).tolist()
                changes = detectChanges(before, after)
                if len(changes) == 0:
                    print("No changes")
                elif len(changes[0]) == 1:
                    print(positionConverter.array2pos(changes[0][0]), "->", positionConverter.array2pos(changes[1][0]))
                else:
                    print("Multiple changes", changes)