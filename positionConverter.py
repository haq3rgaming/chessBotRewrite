numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
letters = ["a", "b", "c", "d", "e", "f", "g", "h"]

def array2pos(array: list) -> str:
    return letters[array[1]] + str(numbers[array[0]])

def pos2array(pos: str) -> list:
    return [numbers.index(int(pos[1])), letters.index(pos[0])]

if __name__ == "__main__":
    print(array2pos([0, 0]))
    print(pos2array("a1"))