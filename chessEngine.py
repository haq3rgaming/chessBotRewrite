from stockfish import Stockfish
from chessboard import Board
import cv2

class ChessEngine:
    def __init__(self, threads: int=4, hash: int=512, skill_level: int=20, minimum_thinking_time: int=20):
        self.engine = Stockfish("stockfish-windows-x86-64.exe")
        self.engine.update_engine_parameters({
            "Threads": threads,
            "Hash": hash,
            "Skill Level": skill_level,
            "Minimum Thinking Time": minimum_thinking_time
            })

    def getBestMove(self, board: Board):
        self.engine.set_fen_position(board.fen())
        return self.engine.get_best_move()
    

if __name__ == "__main__":
    engine = ChessEngine()
    board = Board()
    board.display()
    print(engine.getBestMove(board))
    cv2.waitKey(0)