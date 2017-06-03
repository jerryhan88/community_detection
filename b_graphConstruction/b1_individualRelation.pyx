import __init__
from init_project import *
#
import statsmodels.api as sm
import pandas as pd
import csv


NUM_WORKERS = 11
HOUR1 = 3600

def run(processorID):
    for i, fn in enumerate(os.listdir(dpath['pickupDistance'])):
        if not fn.endswith('.csv'):
            continue
        if i % NUM_WORKERS != processorID:
            continue
        process_driver(fn)


def process_driver(fn):
    ifpath = opath.join(dpath['pickupDistance'], fn)
    df = pd.read_csv(ifpath)
    numWholeRecords = len(df)
    df = df[(df['dwellTime'] != 0) & (df['dwellTime'] < HOUR1)]
    numObservations = len(df)
    _, yyyy, _did1 = fn[:-len('.csv')].split('-')
    ofpath = opath.join(dpath['individualRelation'], 'individualRelation-%s-%s.csv' % (yyyy, _did1))
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
        num_encouters = sum([1 for v in df[_did0] if v !=0])
        # if num_encouters < numObservations * MIN_PICKUP_RATIO:
        #     continue
        y = df['dwellTime']
        X = df[[_did0]]
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

if __name__ == '__main__':
    run(2)