import __init__
from init_project import *



HOUR1 = 3600


def run(processorID, numWorkers=11):
    for i, fn in enumerate(os.listdir(dpath['communityTrip'])):
        if i % numWorkers != processorID:
            continue
        if not fn.endswith('.csv'):
            continue
        _, _, gn = fn[:-len('.csv')].split('-')
        process_group(gn)


def process_group(gn):
    gn = 'G(10)'
    ifpath = opath.join(dpath['communityTrip'], 'communityTrip-2009-%s.csv' % gn)
    ofpath = opath.join(dpath['hotspotDetection'], 'hotspotDetection-2009-%s.pkl' % gn)
    df = pd.read_csv(ifpath)
    df = df[(df['dwellTime'] != 0) & (df['dwellTime'] < HOUR1)]
    base_cns = set('year month day hour time lon lat distance duration fare did zi zj dwellTime'.split())
    prevDrivers = set(df.columns) - base_cns
    df['priorPresence'] = df.apply(lambda row: 1 if sum(row[did0] for did0 in prevDrivers) != 0 else 0, axis=1)
    df['zizj'] = df.apply(lambda row: '%d#%d' % (row['zi'], row['zj']), axis=1)
    whole_zones = set(df['zizj'])
    zoneCoef = {k: [] for k in ['pos', 'neg']}
    for zizj in whole_zones:
        df_zizj = df[(df['zizj'] == zizj)]
        if df_zizj['priorPresence'].sum() == 0:
            continue
        if len(df_zizj) < 2:
            continue
        y = df_zizj['dwellTime']
        X = df_zizj['priorPresence']
        X = sm.add_constant(X)
        res = sm.OLS(y, X, missing='drop').fit()
        pv = res.pvalues['priorPresence']
        coef = res.params['priorPresence']
        if pv < SIGINIFICANCE_LEVEL:
            if coef < 0:
                zoneCoef['neg'] += [(zizj, coef)]
            elif coef > 0:
                zoneCoef['pos'] += [(zizj, coef)]
    with open(ofpath, 'wb') as fp:
        pickle.dump(zoneCoef, fp)


if __name__ == '__main__':
    run(1)





# def process_file(tm, year, gt_fpath):
#     gz_dpath = dpaths[tm, year, 'groupZones']
#     gz_prefix = prefixs[tm, year, 'groupZones']
#     df = pd.read_csv(gt_fpath)
#     assert len(set(df['groupName'])) == 1
#     gn = df['groupName'][0]
#     gz_fpath = '%s/%s%s.pkl' % (gz_dpath, gz_prefix, gn)
#     #
#     df = df[~(np.abs(df[tm] - df[tm].mean()) > (3 * df[tm].std()))]
#     groupZones = {}
#     for zizj, pp_num in df.groupby(['zizj']).sum()['priorPresence'].iteritems():
#         if pp_num < 2:
#             continue
#         zizj_df = df[(df['zizj'] == zizj)]
#         y = zizj_df[tm]
#         X = zizj_df['priorPresence']
#         X = sm.add_constant(X)
#         res = sm.OLS(y, X, missing='drop').fit()
#         if res.params['priorPresence'] < 0 and res.pvalues['priorPresence'] < sig_level:
#             groupZones[zizj] = res.params['priorPresence']
#     save_pickle_file(gz_fpath, groupZones)
#

