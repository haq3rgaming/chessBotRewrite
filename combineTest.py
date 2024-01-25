from chessboard import Board
from chessEngine import ChessEngine
from robot import RobotContext

import serial.tools.list_ports
import cv2

board = Board()
engine = ChessEngine()

port = [port.device for port in serial.tools.list_ports.comports() if port.description.startswith("USB-SERIAL")][0]

board.display()
#cv2.waitKey(0)
print("Start...")

with RobotContext(port, 115200) as robot:
    print("Robot started")
    sequence = robot.Sequencer()
    while not board.termination(): # Whole game loop fix, need to add move with attack
        board.display()
        bestMove = engine.getBestMove(board)
        print(f"Best move: {bestMove}")
        if board.isCapture(bestMove):
            robot.removePiece(bestMove[2:4], interface=sequence)
            sequence.run(robot)
        robot.movePiece(bestMove[0:2], bestMove[2:4], interface=sequence)
        sequence.run(robot)
        board.move(bestMove)
    cv2.destroyAllWindows()