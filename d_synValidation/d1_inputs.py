import __init__
from init_project import *
#




def smallComStructure():
    comStructure = [
        [1],
        [2, 3],
        [4, 5, 6],
    ]
    return comStructure


def midComStructure():
    comStructure = [
        [1],
        [2], [3],
        [4, 5],
        [6, 7, 8],
        [9, 10, 11, 12]
    ]
    return comStructure


def smallNetLowDemand():
    M = [
         [0, 0, 0, 0, 1],
         [0, 0, 0, 1, 1],
         [0, 0, 0, 1, 0],
         [0, 0, 1, 0, 0],
         [1, 0, 0, 0, 0]
         ]
    return M


def smallNetMidDemand():
    M = [
         [0, 0, 0, 1, 1],
         [0, 0, 0, 2, 1],
         [0, 0, 0, 1, 2],
         [0, 0, 1, 0, 0],
         [1, 1, 0, 0, 0]
         ]
    return M


def smallNetHighDemand():
    M = [
         [0, 1, 0, 2, 1],
         [1, 0, 0, 2, 2],
         [2, 0, 0, 1, 2],
         [0, 2, 1, 0, 1],
         [2, 1, 0, 0, 0]
         ]
    return M




def midNetLowDemand():
    M = [
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    ]

    return M


def midNetMidDemand():
    M = [
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 0, 1, 0, 0, 0, 2, 0]
    ]

    return M


def midNetHighDemand():
    M = [
        [0, 0, 1, 2, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 1, 0, 1],
        [0, 2, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 2, 0, 1, 0, 0, 0, 0],
        [3, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [1, 1, 1, 0, 1, 0, 0, 0, 2, 0]
    ]

    return M




# M = gen_M(20, 0.35)
def gen_M(numZones, p):
    M = [[0] * numZones for _ in xrange(numZones)]
    for i in xrange(numZones):
        for j in xrange(numZones):
            if i == j:
                continue
            if random() < p:
                M[i][j] = randint(0, 3)
    return M



f_map_comStructure = {
    'S': smallComStructure,
    'M': midComStructure
}

f_map_netDemand = {
    ('S', 'L'): smallNetLowDemand,
    ('S', 'M'): smallNetMidDemand,
    ('S', 'H'): smallNetHighDemand,
    #
    ('M', 'L'): midNetLowDemand,
    ('M', 'M'): midNetMidDemand,
    ('M', 'H'): midNetHighDemand,
}

prefStrength = np.arange(0.0, 0.5, 0.05)

numSimRun = 50

if __name__ == '__main__':
    pass

