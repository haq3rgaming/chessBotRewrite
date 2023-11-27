import os
os.environ["path"] += r";C:\Program Files\UniConvertor-2.0rc5\dlls"

import chess

import chess.svg
import cv2
from cairosvg import svg2png
import numpy as np


board = chess.Board() # Black is on bottom, white on top

def turn(color: bool=None):
    if color is not None:
        board.turn = color
    return board.turn

def isLegalMove(move):
    try:
        return board.is_legal(board.parse_san(move))
    except chess.IllegalMoveError:
        return False

def move(move):
    board.push_san(move)

def display():
    cv2.imshow("Chessboard", image())

def image():
    svg = chess.svg.board(board=board, size=700)
    png = svg2png(bytestring=svg)
    return cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)