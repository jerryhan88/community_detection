import __init__
from init_project import *

from _utils.logger import get_logger
logger = get_logger()


def Convert_igraph(orignal_graph):
    igid, did_igid = 0, {}
    igG = ig.Graph(directed=True)
    for i, ((did0, did1), w) in enumerate(orignal_graph.iteritems()):
        if w == 0:
            continue
        if i % 1000 == 0:
            logger.info('%.3f handling' % (i / float(len(orignal_graph))))
        if not did_igid.has_key(did0):
            igG.add_vertex(did0)
            did_igid[did0] = igid
            igid += 1
        if not did_igid.has_key(did1):
            igG.add_vertex(did1)
            did_igid[did1] = igid
            igid += 1
        igG.add_edge(did_igid[did0], did_igid[did1], weight=abs(w))
    return igG


def run():
    gp_original_fpath = opath.join(dpath['graphPartition'], 'graphPartition-original.pkl')
    orignal_graph = None
    logger.info('Start graph construction')
    with open(gp_original_fpath, 'rb') as fp:
        orignal_graph = pickle.load(fp)
    fpath = opath.join(dpath['graphComparision'], 'regressionGraph.pkl')
    igG = Convert_igraph(orignal_graph)
    igG.write_pickle(fpath)
    #
    gp_original_fpath = opath.join(dpath['graphPartitionC'], 'graphPartitionC-original.pkl')
    orignal_graph = None
    logger.info('Start graph construction')
    with open(gp_original_fpath, 'rb') as fp:
        orignal_graph = pickle.load(fp)
    fpath = opath.join(dpath['graphComparision'], 'baselineGraph.pkl')
    igG = Convert_igraph(orignal_graph)
    igG.write_pickle(fpath)

if __name__ == '__main__':
    run()