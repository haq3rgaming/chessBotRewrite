import cv2

from chessboard import Board
from chessEngine import ChessEngine

from configManager import ConfigManager
from warp import Warp
from camera import Camera
from mask import Mask
from piecesDetection import piecesDetection
from changesDetection import changesDetection
from change2Move import change2MoveConverter

configManager = ConfigManager("config.json")
config = configManager.loadConfig()

camera = Camera(config["cameraID"])
warper = Warp(config["warpPoints"])
maskerWhite = Mask(config["hsv"]["white"]["upper"], config["hsv"]["white"]["lower"])
maskerBlack = Mask(config["hsv"]["black"]["upper"], config["hsv"]["black"]["lower"])
piecesDetectWhite = piecesDetection()
piecesDetectBlack = piecesDetection()
changesDetectorWhite = changesDetection()
changesDetectorBlack = changesDetection()
converter = change2MoveConverter()

chessboard = Board()
chessEngine = ChessEngine()

cv2.namedWindow("Chessboard", cv2.WINDOW_AUTOSIZE)

image = warper.warp(camera.photo())
changesDetectorWhite.add(piecesDetectWhite.createVerityArrayFromMask(maskerWhite.maskByColor(image)).tolist())
changesDetectorBlack.add(piecesDetectBlack.createVerityArrayFromMask(maskerBlack.maskByColor(image)).tolist())

while True:
    chessboard.display()
    print("Current move:", "White" if chessboard.turn() else "Black")
    key = cv2.waitKey(0)
    if key == -1: continue
    match chr(key):
        case "q":
            print("Quit")
            break
        case " ":
            image = warper.warp(camera.photo())

            if chessboard.turn() == chessboard.WHITE:
                changesDetectorWhite.add(piecesDetectWhite.createVerityArrayFromMask(maskerWhite.maskByColor(image)).tolist())
                detector = changesDetectorWhite
            else:
                changesDetectorBlack.add(piecesDetectBlack.createVerityArrayFromMask(maskerBlack.maskByColor(image)).tolist())
                detector = changesDetectorBlack
            
            if changes := detector.detect():
                tileFrom, tileTo = converter.convert(changes)
                print(tileFrom, "->", tileTo)
                if chessboard.isLegalMove(tileFrom + tileTo):
                    chessboard.move(tileFrom + tileTo)
                else:
                    print("Cannot push, move is illegal")
                    detector.pop()
            else:
                print("Detection failed")
                detector.pop()
        