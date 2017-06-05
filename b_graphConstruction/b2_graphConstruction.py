import __init__
#
'''

'''
#
from community_analysis import dpaths, prefixs
#
from taxi_common.file_handling_functions import check_dir_create, get_all_files, check_path_exist, save_pickle_file, load_pickle_file
from taxi_common.log_handling_functions import get_logger
#
import igraph as ig
import louvain
import csv

logger = get_logger()
numWorker = 64
#
year = '20%02d' % 9
depVar = 'roamingTime'
# depVar = 'interTravelTime'
#
#
if_dpath = dpaths[depVar, 'individual']
if_prefix = prefixs[depVar, 'individual']

of_dpath = dpaths[depVar, 'indPartition']
of_prefix = prefixs[depVar, 'indPartition']


try:
    check_dir_create(of_dpath)
except OSError:
    pass


def run():
    gp_summary_fpath = '%s/%ssummary.csv' % (of_dpath, of_prefix)
    gp_original_fpath = '%s/%soriginal.pkl' % (of_dpath, of_prefix)
    gp_drivers_fpath = '%s/%sdrivers.pkl' % (of_dpath, of_prefix)
    #
    with open(gp_summary_fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(['groupName', 'numDrivers', 'numRelations', 'graphComplexity', 'tieStrength', 'contribution', 'benCon'])
    logger.info('Start handling SP_group_dpath')
    orignal_graph = {}
    for fn in get_all_files(if_dpath, '%ssigRelation-%s-*.pkl' % (if_prefix, year)):
        _, _, _, _, _did1 = fn[:-len('.csv')].split('-')
        sigRelatioin = load_pickle_file('%s/%s' % (if_dpath, fn))
        for _did0, coef in sigRelatioin['pos']:
            did0, did1 = map(int, [_did0, _did1])
            orignal_graph[did0, did1] = coef
    save_pickle_file(gp_original_fpath, orignal_graph)
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
        group_fpath = '%s/%s%s.pkl' % (of_dpath, of_prefix, gn)
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
        gl_img_fpath = '%s/%simg-%s.pdf' % (of_dpath, of_prefix, gn)
        # layout = sg.layout("kk")
        # if len(drivers) < 100:
        #     ig.plot(sg, gl_img_fpath, layout=layout, vertex_label=drivers)
        # else:
        #     ig.plot(sg, gl_img_fpath, layout=layout)
        gn_drivers[gn] = drivers
        gc_fpath = '%s/%scoef-%s.csv' % (of_dpath, of_prefix, gn)
        with open(gc_fpath, 'wt') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow(['groupName', 'did0', 'did1', 'coef'])
            for e in sg.es:
                did0, did1 = [sg.vs[nIndex]['name'] for nIndex in e.tuple]
                coef = e['weight']
                writer.writerow([gn, did0, did1, coef])
    save_pickle_file(gp_drivers_fpath, gn_drivers)

if __name__ == '__main__':
    run()

