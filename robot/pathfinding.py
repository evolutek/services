#!/usr/bin/env python3



def GetNghbrs(p):
    n = []
    n.append(GetPointFromMap(p.x - 1, p.y))
    n.append(GetPointFromMap(p.x + 1, p.y))
    n.append(GetPointFromMap(p.x, p.y - 1))
    n.append(GetPointFromMap(p.x, p.y + 1))
    n.append(GetPointFromMap(p.x - 1, p.y - 1))
    n.append(GetPointFromMap(p.x - 1, p.y + 1))
    n.append(GetPointFromMap(p.x + 1, p.y - 1))
    n.append(GetPointFromMap(p.x + 1, p.y + 1))

    return [x for x in n if x is not None]

def GetPointFromMap(x, y):
    global maap
    valid = x >= Data.robot_radius and x <= Data.mapw - Data.robot_radius and y >= Data.robot_radius and y <= Data.maph - Data.robot_radius
    return maap[x][y] if valid else None

### TEST ###

#Init(20, 20, 0)
#AddObstacle(6, 1, 1, "toto")
#AddObstacle(6, 3, 1)
#AddObstacle(6, 5, 1)
#AddObstacle(6, 7, 1)
#AddObstacle(14, 7, 1)
#AddObstacle(14, 9, 1)
#AddObstacle(14, 11, 1)
#AddObstacle(14, 13, 1)
#AddObstacle(14, 15, 1)
#AddObstacle(14, 17, 1)
#AddObstacle(14, 19, 1)
#AddObstacle(16, 11, 1)
#PathLen(GetPath(2, 4, 16, 18))

### END TEST ###
