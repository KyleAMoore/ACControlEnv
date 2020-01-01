from Aircraft import Aircraft, Bearing
from Airspace import Airspace
from sys import argv

class SimpleAC(Aircraft):
    def msg(self) -> dict:
        return {}

    def calcBearing(self, msg) -> Bearing:
        deltaX = self.dest[0] - self.pos[0]
        deltaY = self.dest[1] - self.pos[1]
        if abs(deltaX) > abs(deltaY):
            if deltaX > 0:
                if self.bearing == Bearing.WEST:
                    return Bearing.SOUTH if deltaY > 0 or self.pos[1] == 0 else Bearing.NORTH
                else:
                    return Bearing.EAST
            else:
                if self.bearing == Bearing.EAST:
                    return Bearing.SOUTH if deltaY > 0 or self.pos[1] == 0 else Bearing.NORTH
                else:
                    return Bearing.WEST
        else:
            if deltaY > 0:
                if self.bearing == Bearing.NORTH:
                    return Bearing.EAST if deltaX > 0 or self.pos[0] == 0 else Bearing.WEST
                else:
                    return Bearing.SOUTH
            else:
                if self.bearing == Bearing.SOUTH:
                    return Bearing.EAST if deltaX > 0 or self.pos[0] == 0 else Bearing.WEST
                else:
                    return Bearing.NORTH

def main(mode=True):
    if mode:
        env = Airspace(10, 10, 1, 4, 1, random=True, acClass=SimpleAC)
        env.run(verbose=True)
        print(env.stats)

    else:
        simulate(20,10000, True)
        simulate(20,10000, False)

def simulate(size, runs, single=True):
    steps = 0
    invalidStarts = 0
    infRuns = 0
    errors = 0
    print("----------Simulating SimpleAC----------")
    for i in range(runs):
        if i%25 == 0: print(f"Executing run {i} of {runs}",end='\r')
        env = Airspace(size,size,1 if single else 2,4,1,True,SimpleAC)
        try:
            env.run()
            for entry in env.stats:
                steps += entry["time"]
        except RuntimeError as e:
            if e.args[1] == 0: invalidStarts += 1
            elif e.args[1] == 1: infRuns += 1
            else: errors += 1
    avg = steps / runs

    print("----------SimpleAC Results----------")
    print(f"Average timesteps: {avg}")
    print(f"Percent invalid initial states: {invalidStarts/runs}")
    print(f"Percent likely infinite loops: {infRuns/runs}")
    print(f"Percent error states after initial: {errors/runs}")

if __name__ == "__main__":
    if len(argv) != 2:
        print("Missing argument. Please run again with either of the arguments --single/-S or --full/-F")
    if argv[1] == "--single" or argv[1] == "-S": main(True)
    elif argv[1] == "--full" or argv[1] == "-F": main(False)
    else: print(f"Unrecognized argument {argv[1]}. Please run again with either of the arguments --single/-S or --full/-F")
