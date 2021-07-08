# This is degueulasse but don't delete it

avg = 48.4
robot = 'pmi'

def gain(g):
    return avg*g, avg*(2-g)

def cmd(g):
    g1,g2 = gain(g)
    print(f'cellaservctl r trajman/{robot}.set_wheels_diameter w1={w1} w2={w2}')

def dist(dist):
    return 2000 - 120 - 55 - dist


