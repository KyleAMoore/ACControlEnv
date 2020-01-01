from enum import Enum
from abc import abstractmethod, ABC

class Bearing(Enum):
    EAST  = 0
    NORTH = 90
    WEST  = 180
    SOUTH = 270

    def opposite(dir1, dir2):
        return ((dir1.value - dir2.value) % 360) == 180

class Aircraft(ABC):
    def __init__(self, Id, initX, initY, initDir, destX, destY):
        self.id = Id
        self.pos = (initX, initY)
        self.dest = (destX, destY)
        self.bearing = initDir
        self.maxX = 0
        self.maxY = 0

    def update(self, msgs) -> None:
        self.bearing = self.calcBearing(msgs)
        self.pos = (
            self.pos[0] + (1 if self.bearing == Bearing.EAST  else
                          -1 if self.bearing == Bearing.WEST  else
                           0),
            self.pos[1] + (1 if self.bearing == Bearing.SOUTH else
                          -1 if self.bearing == Bearing.NORTH else
                           0)
        )

    @abstractmethod
    def msg(self) -> dict:
        pass

    @abstractmethod
    def calcBearing(self, msg) -> Bearing:
        pass

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.id)
