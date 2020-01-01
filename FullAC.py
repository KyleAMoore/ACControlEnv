from Aircraft import Aircraft, Bearing
from Airspace import Airspace
from SimpleAC import SimpleAC
from sys import argv

class FullAC(SimpleAC):
    def msg(self) -> dict:
        return {"pos": self.pos, "dir": self.bearing, "dest": self.dest}

    def calcBearing(self, msg) -> Bearing:
        if len(msg) == 0:
            return super().calcBearing({})
        else:
            deltaX = msg[0]["pos"][0] - self.pos[0]
            deltaY = msg[0]["pos"][1] - self.pos[1]

            if abs(deltaX) > abs(deltaY): #mostly horizontal, go vertical
                if deltaY > 0: #slightly south, go north
                    desBearing = Bearing.NORTH
                elif deltaY < 0: #slightly north, go south
                    desBearing = Bearing.SOUTH
                else: #directly horizontal, just turn right
                    if deltaX > 0: #its east, go south 
                        desBearing = Bearing.SOUTH
                    else: #its west, go north
                        desBearing = Bearing.NORTH
            else: #mostly vertical, go horizontal
                if deltaX > 0: #slightly east, go west
                    desBearing = Bearing.WEST
                elif deltaX < 0: #slight west, go east
                    desBearing = Bearing.EAST
                else: #directly vertical, just turn right
                    if deltaY > 0: #its south, go west
                        desBearing = Bearing.WEST
                    else: #its north, go east
                        desBearing = Bearing.EAST
            
            if self.bearing == Bearing.NORTH and (desBearing == Bearing.SOUTH or self.pos[1] == 0):
                # go horizontally away from other
                desBearing = Bearing.EAST if deltaX < 0 else Bearing.WEST
            elif self.bearing == Bearing.EAST and (desBearing == Bearing.WEST or self.pos[0] == self.maxX):
                # go vertically away from other
                desBearing = Bearing.SOUTH if deltaY < 0 else Bearing.NORTH
            elif self.bearing == Bearing.SOUTH and (desBearing == Bearing.NORTH or self.pos[1] == self.maxY):
                # go horizontally away from other
                desBearing = Bearing.EAST if deltaX < 0 else Bearing.WEST
            elif self.bearing == Bearing.WEST and (desBearing == Bearing.EAST or self.pos[0] == 0):
                # go vertically away from other
                desBearing = Bearing.SOUTH if deltaY < 0 else Bearing.NORTH

            return desBearing

def main(mode=True):
    if mode:
        env = Airspace(10, 10, 2, 4, 1, random=True, acClass=FullAC)
        env.run(verbose=True)
        print(env.stats)

    else:
        simulate(20,10000, True)
        simulate(20,10000, False)

def simulate(size, runs, single=False):
    steps = [0, 0]
    invalidStarts = 0
    infRuns = 0
    errors = 0
    ooas = 0

    numCraft = 1 if single else 2

    print("-----------Simulating FullAC-----------")
    for i in range(runs):
        if i%25 == 0: print(f"Executing run {i} of {runs}",end='\r')
        env = Airspace(size,size,numCraft,4,1,True,FullAC)
        try:
            env.run()
            for entry in env.stats:
                steps[entry["id"]] += entry["time"]
        except RuntimeError as e:
            if e.args[1] == 0:   invalidStarts += 1
            elif e.args[1] == 1: infRuns += 1
            elif e.args[1] == 2: errors += 1
            elif e.args[1] == 4: ooas += 1
            else: print(e.args[0])
    avg = sum(steps)/runs
    avg /= numCraft

    print("-----------FullAC Results-----------")
    print(f"Average timesteps: {avg}")
    print(f"Percent invalid initial states: {invalidStarts/runs}")
    print(f"Percent likely infinite loops: {infRuns/runs}")
    print(f"Percent error states after initial: {errors/runs}")
    print(f"Percent left airspace: {ooas/runs}")

if __name__ == "__main__":
    if len(argv) != 2:
        print("Missing argument. Please run again with either of the arguments --single/-S or --full/-F")
    if argv[1] == "--single" or argv[1] == "-S": main(True)
    elif argv[1] == "--full" or argv[1] == "-F": main(False)
    else: print(f"Unrecognized argument {argv[1]}. Please run again with either of the arguments --single/-S or --full/-F")
