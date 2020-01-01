from Aircraft import Aircraft, Bearing
from random import choice, randint

class Airspace:
    def __init__(self, width, height, numAC, radarRadius, dangerRadius, random = True, acClass=None, aircrafts=set()):
        self.space = [[set() for _ in range(width)] for _ in range(height)]
        self.detRadius = radarRadius
        self.dgrRadius = dangerRadius
        if random:
            self.aircrafts = set()
            for i in range(numAC):
                x = randint(0,width-1)
                y = randint(0,height-1)
                ac = acClass(
                        Id = i,
                        initX = x,
                        initY = y,
                        initDir = choice(list(Bearing)),
                        destX = randint(0,height-1),
                        destY = randint(0,width-1)
                    )
                self.aircrafts.add(ac)
                self.space[y][x].add(ac)
        else:
            self.aircrafts = aircrafts
            for ac in aircrafts:
                if isinstance(ac,Aircraft):
                    self.space[ac.pos[1]][ac.pos[0]].add(ac)
                else:
                    raise TypeError("aircraft set includes an object of type " + str(type(ac)))
        for ac in self.aircrafts:
            ac.maxX = width-1
            ac.maxY = height-1
        
        self.stats = []
        self.rounds = 0
        self.maxRounds = max(height,width)**2

    #returns True if safety is violated in some way by a transition, False otherwise
    def safetyMonitor(self, init=None, result=None, initBear=None, resBear=None):
        for ac in self.aircrafts:
            # more than one aircraft in a single cell
            if len(self.space[ac.pos[1]][ac.pos[0]]) > 1: return True
            # For each aircraft, check if any cells within danger radius contain another aircraft
            if self.dgrRadius >= 1:
                for y in range(max(0,ac.pos[1]-self.dgrRadius),ac.pos[1]+self.dgrRadius+1):
                    for x in range(max(0,ac.pos[0]-self.dgrRadius),ac.pos[0]+self.dgrRadius+1):
                        try:
                            if len(self.space[y][x]) > 0 and ac.pos != (x,y): return True
                        except IndexError:
                            continue
            # If danger radius < 1, check if any aircrafts collided (swapped places)
            elif init is None or result is None:
                start = init[ac]
                stop = result[ac]
                if len(self.space[start[1]][start[0]]) == 1:
                    for otherAC in self.space[start[1]][start[0]]: break
                    if init[otherAC] == stop and result[otherAC] == start:
                        return True
            # Ensure that no 180 degree turns occur
            if initBear and resBear: return Bearing.opposite(initBear[ac], resBear[ac]) 
        return False

    def update(self):
        self.rounds += 1
        init = {ac: ac.pos for ac in self.aircrafts}
        initBear = {ac: ac.bearing for ac in self.aircrafts}
        msgs = [ac.msg() for ac in self.aircrafts]
        for ac in self.aircrafts:
            inRadius = []
            for y in range(ac.pos[1]-self.detRadius,ac.pos[1]+self.detRadius+1):
                for x in range(ac.pos[0]-self.detRadius,ac.pos[0]+self.detRadius+1):
                    try:
                        if y < 0 or x < 0: raise IndexError
                        if len(self.space[y][x]) == 1:
                            for item in self.space[y][x]:
                                if item != ac: inRadius.append(item)
                                break # most efficient way of viewing, but not removing single element in set
                    except IndexError:
                        continue
            ac.update([msgs[otherAC.id] for otherAC in inRadius])            
        res = {ac: ac.pos for ac in self.aircrafts}
        resBear = {ac: ac.bearing for ac in self.aircrafts}

        # update self.space
        for ac in self.aircrafts:
            try:
                if res[ac][1] < 0 or res[ac][0] < 0: raise IndexError
                if res[ac] == init[ac]: raise ValueError
                self.space[res[ac][1]][res[ac][0]].add(ac)
                self.space[init[ac][1]][init[ac][0]].remove(ac)
            except IndexError:
                raise RuntimeError("Aircraft has left the airspace", 4)
            except ValueError:
                raise RuntimeError("Aircraft did not move during a timestep", 3)

        if self.safetyMonitor(init, res, initBear, resBear):
            raise RuntimeError("Safety Requirements Violated", 2)
        if self.rounds > self.maxRounds:
            raise RuntimeError("Likely infinite loop", 1)

        # remove aircraft that reached their destination
        for ac in list(self.aircrafts):
            if ac.pos == ac.dest:
                self.aircrafts.remove(ac)
                self.space[ac.pos[1]][ac.pos[0]].remove(ac)
                self.stats.append({"id": ac.id, "time": self.rounds})

    def run(self, verbose=False):
        if verbose: print(self,end="\n\n")
        if self.safetyMonitor(): raise RuntimeError("Invalid (unsafe) initial state", 0)
        for ac in list(self.aircrafts):
            if ac.pos == ac.dest:
                self.aircrafts.remove(ac)
                self.space[ac.pos[1]][ac.pos[0]].remove(ac)
                self.stats.append({"id": ac.id, "time": self.rounds})
        while len(self.aircrafts) > 0:
            self.update()
            if verbose:
                print(f"{self.rounds}{'-' * ((len(self.space[0])*3) - len(str(self.rounds)))}")
                print(self)

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        dests = {}
        for ac in self.aircrafts:
            if(ac.dest not in dests):
                dests[ac.dest] = chr(65+ac.id)
            else:
                dests[ac.dest] = "#"

        retStr = ""
        for y in range(len(self.space)):
            for x in range(len(self.space[y])):
                if len(self.space[y][x]) == 1:
                    for ac in self.space[y][x]: break
                    retStr += f" {ac} "
                elif len(self.space[y][x]) > 1:
                    retStr += " X "
                else:
                    try:
                        retStr += f" {dests[(x,y)]} "
                    except KeyError:
                        retStr += " . "
            retStr += "\n"
        return retStr[:-1]
