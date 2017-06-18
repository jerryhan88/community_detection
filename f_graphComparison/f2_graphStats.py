import __init__
from init_project import *


def run():
    wholeDrivers = set()
    for fn in os.listdir(dpath['driverTrip']):
        if not fn.endswith('.csv'):
            continue
        _, _, _did = fn[:-len('.csv')].split('-')
        wholeDrivers.add(int(_did))
    reg_fpath = opath.join(dpath['graphComparision'], 'regressionGraph.pkl')
    base_fpath = opath.join(dpath['graphComparision'], 'baselineGraph.pkl')
    regressionGraph, baseGraph = map(ig.Graph.Read_Pickle, [reg_fpath, base_fpath])
    numRegNodes, numRegEdges = len(regressionGraph.vs), len(regressionGraph.es)
    numBaseNodes, numBaseEdges = len(baseGraph.vs), len(baseGraph.es)

    whole
    detectedDrivers
    density
    numComs



if __name__ == '__main__':
    run()