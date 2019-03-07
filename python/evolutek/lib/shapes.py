from math import sqrt, cos, sin, atan, acos, degrees
from statistics import pstdev, mean

def angle(p0, p1, p2):
    a = pow(p1.x - p0.x, 2) + pow(p1.y - p0.y, 2)
    b = pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2)
    c = pow(p2.x - p0.x, 2) + pow(p2.y - p0.y, 2)
    return degrees(acos((a + b - c) / sqrt(4 * a * b)))

def dist(a, b):
    return sqrt(pow(b.x - a.x, 2) + pow(b.y - a.y, 2))


def seg_dist(a, b, c): #distance from point c to segment ab
    sx = b.x - a.x
    sy = b.y - a.y
    dsq = sx * sx + sy * sy
    u = ((c.x - a.x) * sx + (c.y - a.y) * sy) / float(dsq)
    if u > 1 :
        u = 1
    elif u < 0 :
        u = 0
    x = a.x + u * sx
    y = a.y + u * sy
    dx = x - c.x
    dy = y - c.y
    return sqrt(dx * dx + dy * dy)

def is_circle(data):
    d1 = data[0]
    d2 = data[len(data) // 2]
    d3 = data[-1]
    d = dist(d1, d2)
    x = seg_dist(d1, d3, d2)
    print("d: %d, x: %d" % (d, x))
    if x < 0.2 * d or x > 0.7 * d:
        return False
    print("\033[1;31mshape is a potential circle!\033[1;m")
    angles = [None] * (len(data) - 3)
    print(d1)
    for p in range(1, len(data) - 2):
        print(data[p])
        angles[p - 1] = angle(d1, data[p], d3)
    m = mean(angles)
    print(d3)
    print(angles)
    print("mean: ", m, "stdev: ", pstdev(angles))
    return  90 < m and 135 > m and pstdev(angles) < 8

def circle(a, b, c):
    dax = b.x - a.x
    day = b.y - a.y
    dbx = c.x - b.x
    dby = c.y - b.y

    aslope = day/dax
    bslope = dby/dbx

    x = (aslope * bslope * (a.y - c.y) + bslope * (a.x + c.x) - aslope * (b.x + c.x)) / (2 * (bslope - aslope))
    y = -(x - (a.x + b.x) / 2) / aslope + (a.y + b.y) / 2
    return ("circle", Point(x, y), a)

def sq_centers(a, b): #computes the centers of a square containing that segment
    dx = b.x - a.x
    dy = b.y - a.y

    c1x = (dx + dy) / 2
    c1y = (dy - dx) / 2

    c2x = (dx - dy) / 2
    c2y = (dy + dx) / 2

    c1 = Point(a.x + c1x, a.y + c1y)
    c2 = Point(a.x + c2.x, a.y + c2.y)

    if (c1.y) > (c2.y):
        return (c2, c1)
    else:
        return (c1, c2)

def square(data):
    if len(data) == 1:
        (c1, c2) = sq_centers(data[0][1], data[0][2])
        if pos.y > c1.y:
            return(c1)
        else:
            return(c2)
    else:
        seg = None
        if dist(data[0][1], data[0][2]) > dist(data[1][1], data[1][2]):
            seg = (data[0][1], data[0][2])
        else:
            seg = (data[1][1], data[1][2])
        (c1, c2) = sq_centers(seg[0], seg[1])
        if pos.y > c1.y:
            return(c1)
        else:
            return(c2)

def parse_lines(data, pos):
    if dist(data[0], data[-1]) < 20:
        return [("line", data[0], data[-1])]
    dist = list(map(seg_dist(data[0], data[-1]), data[1,-2]))
    m = max(dist)
    if m > 3:
        ret = parse_lines(data[0, dist.index(m) + 1]).extend(parse_lines[dist.index(m) + 1, -1])
        if len(ret) < 3:
            return square(ret)
        else:
            return ret
    else:
        return [("line", data[0], data[-1])]
    
    
def parse_shapes(data, pos):
    if is_circle(data):
        return [circle(data[0], data[len(data) / 2], data[-1])]
    else:
        return parse_lines(data)

def get_center(data, pos):
    if data[0] == "circle":
        return data[1];
    else:
        return square(data, pos)