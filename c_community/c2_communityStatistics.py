import __init__
from init_project import *
#
from _utils.logger import get_logger
logger = get_logger()


def run(processorID, numWorkers=11):
    for i, fn in enumerate([fn for fn in os.listdir(dpath['communityTripWP']) if fnmatch(fn, '*.csv')]):
        if not fn.endswith('.csv'):
            continue
        _, _, gn = fn[:-len('.csv')].split('-')
        if i % numWorkers != processorID:
            continue
        process_group(gn)

def process_group(gn):
    fpath = opath.join(dpath['communityTrip'], 'communityTrip-2009-%s.csv' % gn)
    df = pd.read_csv(fpath)
    base_cns = 'year month day hour time lon lat distance duration fare did zi zj dwellTime'.split()
    comDrivers = [cn for cn in df.columns if cn not in base_cns]
    df['comPriorPresence'] = df.apply(lambda row: 1 if sum([row[_did] for _did in comDrivers]) != 0 else 0, axis=1)
    #
    numDrivers = len(set(df['did']))
    numTrips = df.groupby(['year', 'month', 'day', 'did']).count().reset_index()['fare'].mean()
    distance = df.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['distance'].mean()
    duration = df.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['duration'].mean()
    fare = df.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['fare'].mean()
    distance_trip = distance / float(numTrips)
    duration_trip = (duration) / 3600.0
    fare_trip = fare / float(numTrips)
    spendingTime = gt_df.groupby(['year', 'month', 'day', 'did']).sum().reset_index()['spendingTime'].mean()
    spendingTime_trip = spendingTime / float(numTrips)
    
    
    
    
    if gn == 'X':
        pass
    


if __name__ == '__main__':
    run(0)

