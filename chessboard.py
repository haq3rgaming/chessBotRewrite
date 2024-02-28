import os
os.environ["path"] += r";C:\Program Files\UniConvertor-2.0rc5\dlls"

import chess

import chess.svg
import cv2
from cairosvg import svg2png
import numpy as np

class Board:
    WHITE = True
    BLACK = False

    def __init__(self) -> None:
        self.board = chess.Board() # Black is on bottom, white on top

    def fen(self):
        return self.board.fen()

    def turn(self, color: bool=None):
        if color is not None: self.board.turn = color
        return self.board.turn

    def isLegalMove(self, move):
        try:
            return self.board.is_legal(self.board.parse_san(move))
        except chess.IllegalMoveError:
            return False

    def isCapture(self, move: str):
        return self.board.is_capture(self.board.parse_san(move))

    def move(self, move):
        try:
            self.board.push_san(move)
            return True
        except Exception:
            return False

    def termination(self):
        return self.board.is_game_over()

    def result(self):
        return self.board.result()

    def image(self, **kwargs):
        svg = chess.svg.board(board=self.board, size=700, **kwargs)
        png = svg2png(bytestring=svg)
        return cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)

    def display(self, **kwargs):
        cv2.imshow("Chessboard", self.image(**kwargs))
        cv2.waitKey(1)

