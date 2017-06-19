import __init__
from init_project import *
#


def run():
    pass





def comStructure0():
    pass


def comStructure1():
    comStructure = [
        [1],
        [2], [3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12]
    ]
    return comStructure

def demandDist0():
    M = [
         [0, 0, 0, 1, 1],
         [0, 0, 0, 2, 1],
         [0, 0, 0, 1, 2],
         [0, 0, 1, 0, 0],
         [1, 1, 0, 0, 0]
         ]
    return M

def demandDist1():
    M = [
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 0, 1, 0, 0, 0, 0, 0]
    ]
    # M = gen_M(20, 0.35)
    return M


def gen_M(numZones, p):
    M = [[0] * numZones for _ in xrange(numZones)]
    for i in xrange(numZones):
        for j in xrange(numZones):
            if i == j:
                continue
            if random() < p:
                M[i][j] = randint(0, 3)
    return M


if __name__ == '__main__':
    run(3)
