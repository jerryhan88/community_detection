import __init__
from init_project import *
#
from _utils.logger import get_logger
#
import statsmodels.api as sm
import pickle
import pandas as pd
import numpy as np
import csv

logger = get_logger()


def run():
    for fn in os.listdir(dpath['agtPresence']):
        if not fn.endswith('.csv'):
            continue
        process_driver(fn)

def process_driver(fn):
    logger.info('handling %s' % fn)
    _, _seedNum, _aid1 = fn[:-len('.csv')].split('-')
    fpath =opath.join(dpath['agtPresence'], fn)
    df = pd.read_csv(fpath)
    numObservations = len(df)
    ofpath = opath.join(dpath['agtRelation'], 'agtRelation-%s-%s.csv' % (_seedNum, _aid1))
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = ['aid',
                  'numObservations', 'numPrevAgents',
                  'numSigRelationship',
                  'numPosCoef', 'numNegCoef',
                  'sigPosRelation', 'sigNegRelation']
        writer.writerow(header)
    cns = 'aid zid reward'.split()
    prevAgents = [cn for cn in df.columns if cn not in cns]
    sigRelatioin = {k: [] for k in ['pos', 'neg']}
    for _agt0 in prevAgents:
        num_encouters = 0
        zones = set()
        for encounter, zid in df[[_agt0, 'zid']].values:
            if encounter != 0:
                num_encouters += 1
                zones.add(zid)
        agt0_df = df[[_agt0, 'zid', 'reward']]
        if len(agt0_df) == 0:
            continue
        for zid in zones:
            agt0_df['z%d' % zid] = np.where(agt0_df['zid'] == zid, 1, 0)
        if num_encouters < len(zones) + 1 + 1:
            continue

        y = agt0_df['reward']
        X = agt0_df[[_agt0] + ['z%d' % zid for zid in zones][:-1]]
        X = sm.add_constant(X)
        res = sm.OLS(y, X, missing='drop').fit()
        pv = res.pvalues[_agt0]
        coef = res.params[_agt0]
        if pv < SIGINIFICANCE_LEVEL:
            if coef < 0:
                sigRelatioin['neg'] += [(_agt0, coef)]
            elif coef > 0:
                sigRelatioin['pos'] += [(_agt0, coef)]
    with open(ofpath, 'a') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_row = [_aid1,
                   numObservations, len(prevAgents),
                   len(sigRelatioin['pos']) + len(sigRelatioin['neg']),
                   len(sigRelatioin['pos']), len(sigRelatioin['neg']),
                   '|'.join([_agt0 for _agt0, _ in sigRelatioin['pos']]), '|'.join([_agt0 for _agt0, _ in sigRelatioin['neg']])]
        writer.writerow(new_row)



if __name__ == '__main__':
    run()
