import __init__
from init_project import *
#
from _utils.logger import get_logger
logger = get_logger()

HOUR1 = 3600


def run(processorID, numWorkers=11):
    for i, fn in enumerate([fn for fn in os.listdir(dpath['communityTrip']) if fnmatch(fn, '*.csv')]):
        if not fn.endswith('.csv'):
            continue
        _, _, gn = fn[:-len('.csv')].split('-')
        if i % numWorkers != processorID:
            continue
        process_group(gn)


def process_group(gn):
    ofpath = opath.join(dpath['communityStats'], 'communityStats-2009-%s.csv' % gn)
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(['comName',
                         'numDrivers', 'graphDensity',
                         'numTripsPD', 'operationHourPD', 'durationPD', 'vacantRate',
                         'farePD', 'dwellTimePT', 'dwellTimePriPT',
                         'avgEdgeW',
                         'numRelations','distancePD', 'dwellTimePD',
                         'distancePT', 'durationPT', 'farePT'
                         ])
    #
    graph_fpath = opath.join(dpath['graphPartition'], 'graphPartition-%s.pkl' % gn)
    igG = ig.Graph.Read_Pickle(graph_fpath)
    numNodes, numEdges = len(igG.vs), len(igG.es)
    graphDensity = numEdges / float(numNodes * (numNodes - 1))
    avgEdgeW = (sum([e['weight'] for e in igG.es]) / 60.0) / numEdges
    #
    trip_fpath = opath.join(dpath['communityTrip'], 'communityTrip-2009-%s.csv' % gn)
    proDur_fpath = opath.join(dpath['communityProdDuration'], 'communityProdDuration-2009-%s.csv' % gn)
    #
    df_trip, df_proDur = map(pd.read_csv, [trip_fpath, proDur_fpath])
    df_tripF = df_trip[(df_trip['dwellTime'] != 0) & (df_trip['dwellTime'] < HOUR1)]
    base_cns = set('year month day hour time lon lat distance duration fare did zi zj dwellTime'.split())
    prevDrivers = set(df_trip.columns) - base_cns
    df_tripF['priorPresence'] = df_tripF.apply(lambda row: 1 if sum(row[_did] for _did in prevDrivers) !=0 else 0, axis=1)
    df_priTrip = df_tripF[(df_tripF['priorPresence'] == 1)]
    numTrips = df_trip.groupby(['year', 'month', 'day', 'did']).count().reset_index()['fare'].mean()
    numTripsF = df_tripF.groupby(['year', 'month', 'day', 'did']).count().reset_index()['fare'].mean()
    distance = df_trip.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['distance'].mean()
    duration = df_trip.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['duration'].mean()
    fare = df_trip.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['fare'].mean()
    dwellTime = df_tripF.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['dwellTime'].mean()
    operatingH = df_proDur.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['pro-dur'].mean()
    #
    operatingHourPD = operatingH / 60.0
    distancePD = distance
    durationPD = duration / 3600.0
    farePD = fare / 100.0
    dwellTimePD = dwellTime / 60.0
    #
    distancePT = distance / float(numTrips)
    durationPT = (duration / 3600.0) / float(numTrips)
    farePT = (fare / 100.0) / float(numTrips)
    dwellTimePT = (dwellTime / 60.0) / float(numTripsF)
    dwellTimePriPT = df_priTrip['dwellTime'].mean() / 60.0
    #
    with open(ofpath, 'a') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow([gn,
                         numNodes, graphDensity,
                         numTrips, operatingHourPD, durationPD, (operatingHourPD - durationPD) / float(operatingHourPD),
                         farePD, dwellTimePT, dwellTimePriPT,
                         avgEdgeW,
                         numEdges, distancePD, dwellTimePD,
                         distancePT, durationPT, farePT])

if __name__ == '__main__':
    run(3)

