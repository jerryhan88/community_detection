import __init__
from init_project import *
#
from _utils.logger import get_logger
#
#
import igraph as ig
import pickle
import louvain
import csv

logger = get_logger()


def run():
    gp_summary_fpath = opath.join(dpath['graphPartition'], 'graphPartition-summary.csv')
    gp_original_fpath = opath.join(dpath['graphPartition'], 'graphPartition-original.pkl')
    gp_drivers_fpath = opath.join(dpath['graphPartition'], 'graphPartition-drivers.pkl')
    #
    with open(gp_summary_fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(['groupName', 'numDrivers', 'numRelations', 'graphComplexity', 'tieStrength', 'contribution', 'benCon'])
    logger.info('Start handling SP_group_dpath')
    orignal_graph = {}
    for i, fn in enumerate(os.listdir(dpath['individualRelationF'])):
        if not fn.endswith('.csv'):
            continue
        _, _year, _did1 = fn[:-len('.csv')].split('-')
        fpath = opath.join(dpath['individualRelationF'], 'sigRelation-%s-%s.pkl' % (_year, _did1))
        if not opath.exists(fpath):
            continue
        sigRelatioin = None
        with open(fpath, 'rb') as fp:
            sigRelatioin = pickle.load(fp)
        for _did0, coef in sigRelatioin['neg']:
            did0, did1 = map(int, [_did0, _did1])
            orignal_graph[did0, did1] = coef
    with open(gp_original_fpath, 'wb') as fp:
        pickle.dump(orignal_graph, fp)
    #
    igid, did_igid = 0, {}
    igG = ig.Graph(directed=True)
    for i, ((did0, did1), w) in enumerate(orignal_graph.iteritems()):
        if not did_igid.has_key(did0):
            igG.add_vertex(did0)
            did_igid[did0] = igid
            igid += 1
        if not did_igid.has_key(did1):
            igG.add_vertex(did1)
            did_igid[did1] = igid
            igid += 1
        igG.add_edge(did_igid[did0], did_igid[did1], weight=abs(w))
    logger.info('Partitioning')
    part = louvain.find_partition(igG, method='Modularity', weight='weight')
    logger.info('Each group pickling and summary')
    gn_drivers = {}
    for i, sg in enumerate(part.subgraphs()):
        gn = 'G(%d)' % i
        group_fpath = opath.join(dpath['graphPartition'], 'graphPartitioin-%s.pkl' % gn)
        sg.write_pickle(group_fpath)
        #
        drivers = [v['name'] for v in sg.vs]
        weights = [e['weight'] for e in sg.es]
        graphComplexity = len(weights) / float(len(drivers))
        tie_strength = sum(weights) / float(len(drivers))
        contribution = sum(weights) / float(len(weights))
        benCon = tie_strength / float(len(drivers))
        with open(gp_summary_fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([gn, len(drivers), len(weights), graphComplexity, tie_strength, contribution, benCon])
        gl_img_fpath = opath.join(dpath['graphPartition'], 'graphPartitioin-img-%s.pdf' % gn)
        layout = sg.layout("kk")
        if len(drivers) < 100:
            ig.plot(sg, gl_img_fpath, layout=layout, vertex_label=drivers)
            pass
        else:
            ig.plot(sg, gl_img_fpath, layout=layout)
            pass
        gn_drivers[gn] = drivers
        gc_fpath = opath.join(dpath['graphPartition'], 'graphPartitioin-coef-%s.pkl' % gn)
        with open(gc_fpath, 'wt') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow(['groupName', 'did0', 'did1', 'coef'])
            for e in sg.es:
                did0, did1 = [sg.vs[nIndex]['name'] for nIndex in e.tuple]
                coef = e['weight']
                writer.writerow([gn, did0, did1, coef])
    with open(gp_drivers_fpath, 'wb') as fp:
        pickle.dump(gn_drivers, fp)


if __name__ == '__main__':
    run()

