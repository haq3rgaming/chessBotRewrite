from positionConverter import array2pos, pos2array

class change2MoveConverter:
    def __init__(self) -> None:
        pass

    def convert(self, changes: list) -> str:
        tileFrom = array2pos(changes[0][0])
        tileTo = array2pos(changes[1][0])
        return tileFrom, tileTo