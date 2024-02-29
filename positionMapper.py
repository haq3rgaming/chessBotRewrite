hardCoded = {
  "a4": [70, -129],
  "a5": [-70, 128]
  }

class Mapper():
    def __init__(self, intervalFrom: tuple, intervalTo: tuple) -> None:
        self.intervalFrom = intervalFrom
        self.intervalTo = intervalTo
    
    def map(self, value: float) -> float:
        a = (value - self.intervalFrom[0]) * (self.intervalTo[1] - self.intervalTo[0])
        b = (self.intervalFrom[1] - self.intervalFrom[0])
        return  a / b + self.intervalTo[0]
    

if __name__ == "__main__":
    mapperPos = Mapper((1, 8), (4, 27)) # X axis
    mapperNeg = Mapper((1, 8), (-11.5, 12.5)) # Y axis
    print(mapperPos.map(4))
    print(mapperNeg.map(4))