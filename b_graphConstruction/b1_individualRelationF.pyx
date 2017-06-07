import __init__
from init_project import *
#
from _utils.logger import get_logger
#
from traceback import format_exc
import statsmodels.api as sm
import pickle
import pandas as pd
import numpy as np
import csv

logger = get_logger()

# NUM_WORKERS = 11
NUM_WORKERS = 64

HOUR1 = 3600

def run(processorID):
    for i, fn in enumerate(os.listdir(dpath['pickupDistance'])):
        if not fn.endswith('.csv'):
            continue
        if i % NUM_WORKERS != processorID:
            continue
        process_driver(fn)


def process_driver(fn):
    logger.info('handling %s' % fn)
    try:
        ifpath = opath.join(dpath['pickupDistance'], fn)
        df = pd.read_csv(ifpath)
        numWholeRecords = len(df)
        df = df[(df['dwellTime'] != 0) & (df['dwellTime'] < HOUR1)]
        numObservations = len(df)
        _, yyyy, _did1 = fn[:-len('.csv')].split('-')
        ofpath = opath.join(dpath['individualRelationF'], 'individualRelationF-%s-%s.csv' % (yyyy, _did1))
        sig_fpath = opath.join(dpath['individualRelationF'], 'sigRelation-%s-%s.pkl' % (yyyy, _did1))
        if opath.exists(sig_fpath):
            return None
        with open(ofpath, 'wt') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            header = ['did', 'numWholeRecords',
                      'numObservations', 'numPrevDrivers',
                      'numSigRelationship',
                      'numPosCoef', 'numNegCoef',
                      'sigPosRelation', 'sigNegRelation']
            writer.writerow(header)
        cns = 'year month day hour time lon lat distance duration fare did zi zj dwellTime'.split()
        prevDrivers = [cn for cn in df.columns if cn not in cns]
        sigRelatioin = {k: [] for k in ['pos', 'neg']}
        for _did0 in prevDrivers:
            num_encouters = 0
            zones = set()
            for encounter, zi, zj in df[[_did0, 'zi', 'zj']].values:
                if encounter != 0:
                    num_encouters += 1
                    zones.add('%d#%d' % (zi, zj))
            did0_df = df[[_did0, 'zi', 'zj', 'dwellTime']]
            if len(did0_df) == 0:
                continue
            did0_df['zizj'] = did0_df.apply(lambda row: '%d#%d' % (row['zi'], row['zj']), axis=1)
            for zizj in zones:
                did0_df['z'+zizj] = np.where(did0_df['zizj'] == zizj, 1, 0)
            if num_encouters < len(zones) + 1 + 1:
                continue

            y = did0_df['dwellTime']
            X = did0_df[[_did0] + ['z'+zizj for zizj in zones]]
            X = sm.add_constant(X)
            res = sm.OLS(y, X, missing='drop').fit()
            pv = res.pvalues[_did0]
            coef = res.params[_did0]
            if pv < SIGINIFICANCE_LEVEL:
                if coef < 0:
                    sigRelatioin['neg'] += [(_did0, coef)]
                elif coef > 0:
                    sigRelatioin['pos'] += [(_did0, coef)]
        with open(ofpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [_did1, numWholeRecords,
                       numObservations, len(prevDrivers),
                       len(sigRelatioin['pos']) + len(sigRelatioin['neg']),
                       len(sigRelatioin['pos']), len(sigRelatioin['neg']),
                       '|'.join([_did0 for _did0, _ in sigRelatioin['pos']]), '|'.join([_did0 for _did0, _ in sigRelatioin['neg']])]
            writer.writerow(new_row)
        #
        with open(sig_fpath, 'wb') as fp:
            pickle.dump(sigRelatioin, fp)
    except Exception as _:
        import sys
        with open('%s_%s.txt' % (sys.argv[0], fn), 'w') as f:
            f.write(format_exc())
        raise
    logger.info('end %s' % fn)


if __name__ == '__main__':
    # run(1)
    process_driver('pickupDistance-2009-13959.csv')