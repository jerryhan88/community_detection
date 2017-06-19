import __init__
from init_project import *


def run():
    ofpath = opath.join(dpath['graphStats'], 'graphStats-summary.csv')
    #

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

    numRegCom = len([fn for fn in os.listdir(dpath['graphPartition'])
                     if fnmatch(fn, 'graphPartition-G*.pkl')])
    numBaseCom = len([fn for fn in os.listdir(dpath['graphPartitionC'])
                      if fnmatch(fn, 'graphPartitionC-G*.pkl')])

    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(['way', 'numWholeDrivers',
                         'numIncludedDrivers', 'numRelations',
                         'graphDensity',
                         'numDetectedCommunity', 'avgNumMebers'])
        writer.writerow(['regression', len(wholeDrivers),
                           numRegNodes, numRegEdges,
                           numRegEdges / float(numRegNodes * (numRegNodes - 1)),
                           numRegCom,  numRegNodes/ float(numRegCom )
                           ])
        writer.writerow(['count', len(wholeDrivers),
                         numBaseNodes, numBaseEdges,
                         numBaseEdges / float(numBaseNodes* (numBaseNodes - 1)),
                         numBaseCom, numBaseNodes/ float(numBaseCom )
                         ])


if __name__ == '__main__':
    run()