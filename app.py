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

import serial.tools.list_ports
from chessEngine import ChessEngine
from robot import RobotContext

configManager = ConfigManager("config.json")
config = configManager.loadConfig()

camera = Camera(config["cameraID"])
warper = Warp(config["warpPoints"])
maskerWhite = Mask(config["hsv"]["white"]["upper"], config["hsv"]["white"]["lower"])
maskerBlack = Mask(config["hsv"]["black"]["upper"], config["hsv"]["black"]["lower"])
piecesDetectWhite = piecesDetection()
changesDetectorWhite = changesDetection()
converter = change2MoveConverter()

chessboard = Board()
chessEngine = ChessEngine()

cv2.namedWindow("Chessboard", cv2.WINDOW_AUTOSIZE)

port = [port.device for port in serial.tools.list_ports.comports() if port.description.startswith("USB-SERIAL")][0]
capture = False

with RobotContext(port, 115200) as robot:
    print("Robot started")
    robot.dock()
    print("Press any key when docked!")
    if chr(cv2.waitKey(0)) == "q":
        print("Quit")
        exit()
    image = warper.warp(camera.photo())
    changesDetectorWhite.add(piecesDetectWhite.createVerityArrayFromMask(maskerWhite.maskByColor(image)).tolist())

    # main loop
    while not chessboard.termination():
        chessboard.display()
        if capture:
            print("Piece removed, don't move any pieces! Press any key when docked!")
            if chr(cv2.waitKey(0)) == "q":
                print("Quit")
                exit()
            image = warper.warp(camera.photo())
            changesDetectorWhite.add(piecesDetectWhite.createVerityArrayFromMask(maskerWhite.maskByColor(image)).tolist())
            capture = False
        print("Current move:", "White" if chessboard.turn() else "Black")
        
        if chessboard.turn() == chessboard.WHITE:
            if chr(cv2.waitKey(0)) == "q":
                print("Quit")
                break

            image = warper.warp(camera.photo())
            changesDetectorWhite.add(piecesDetectWhite.createVerityArrayFromMask(maskerWhite.maskByColor(image)).tolist())
            detector = changesDetectorWhite
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
        else:
            move = chessEngine.getBestMove(chessboard)
            print("Engine move:", move)
            if chessboard.isCapture(move):
                capture = True
                robot.removePiece(move[2:4])
            robot.movePiece(move[0:2], move[2:4])
            robot.dock()
            chessboard.move(move)
    print("Game terminated")
    print(chessboard.result())

cv2.destroyAllWindows()
            