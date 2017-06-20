import __init__
from init_project import *
#
from _utils.logger import get_logger
#

logger = get_logger()


def do_regression(sn, ps, cs, ns, da):
    regExp = 'presenceBinary-seed(%d)-ps(%.2f)-cs(%s)-ns(%s)-da(%s)-*.csv' % (sn, ps, cs, ns, da)
    for fn in os.listdir(dpath['presenceBinary']):
        if not fnmatch(fn, regExp):
            continue
        logger.info('handling %s' % fn)
        fpath =opath.join(dpath['presenceBinary'], fn)
        df = pd.read_csv(fpath)
        numObservations = len(df)
        ofpath = opath.join(dpath['driverRelation'], fn.replace('presenceBinary', 'driverRelation'))

        _did = fn[:-len('.csv')].split('-')[-1]
        did = int(_did[len('did('):-len(')')])
        with open(ofpath, 'wt') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            header = ['did',
                      'numObservations', 'numPrevAgents',
                      'numSigRelationship',
                      'numPosCoef', 'numNegCoef',
                      'sigPosRelation', 'sigNegRelation']
            writer.writerow(header)
        prevDrivers = [cn for cn in df.columns if cn not in 'did zid dwellTime'.split()]
        sigRelatioin = {k: [] for k in ['pos', 'neg']}
        for _did0 in prevDrivers:
            num_encouters = 0
            zones = set()
            for encounter, zid in df[[_did0, 'zid']].values:
                if encounter != 0:
                    num_encouters += 1
                    zones.add(zid)
            did0_df = df[[_did0, 'zid', 'dwellTime']]
            if len(did0_df) == 0:
                continue
            for zid in zones:
                did0_df['z%d' % zid] = np.where(did0_df['zid'] == zid, 1, 0)
            if num_encouters < len(zones) + 1 + 1:
                continue
            if num_encouters < numObservations * 0.05:
                continue
            y = did0_df['dwellTime']
            X = did0_df[[_did0] + ['z%d' % zid for zid in zones][:-1]]
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
            new_row = [did,
                       numObservations, len(prevDrivers),
                       len(sigRelatioin['pos']) + len(sigRelatioin['neg']),
                       len(sigRelatioin['pos']), len(sigRelatioin['neg']),
                       '|'.join([_did0 for _did0, _ in sigRelatioin['pos']]), '|'.join([_did0 for _did0, _ in sigRelatioin['neg']])]
            writer.writerow(new_row)


if __name__ == '__main__':
    pass
