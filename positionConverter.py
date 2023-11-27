numbers = [8, 7, 6, 5, 4, 3, 2, 1]
letters = ["a", "b", "c", "d", "e", "f", "g", "h"]

def array2pos(array: list) -> str:
    return letters[array[1]] + str(numbers[array[0]])

def pos2array(pos: str) -> list:
    return [numbers.index(int(pos[1])), letters.index(pos[0])]

if __name__ == "__main__":
    print(array2pos([0, 0]))
    print(pos2array("a1"))