import __init__
from init_project import *
#
from _utils.logger import get_logger
logger = get_logger()


def run(processorID, numWorkers=11):
    xComDrivers = set()
    for fn in os.listdir(dpath['driverTrip']):
        if not fn.endswith('.csv'):
            continue
        _, _, _did = fn[:-len('.csv')].split('-')
        xComDrivers.add(int(_did))
    #
    for i, fn in enumerate(os.listdir(dpath['graphPartition'])):
        if not fn.endswith('.pkl'):
            continue
        if 2 < len(fn.split('-')):
            continue
        _, gn = fn[:-len('.pkl')].split('-')
        if gn in ['original', 'drivers']:
            continue
        ifpath = opath.join(dpath['graphPartition'], 'graphPartition-%s.pkl' % gn)
        igG = ig.Graph.Read_Pickle(ifpath)
        comDrivers = set(v['name'] for v in igG.vs)
        xComDrivers = xComDrivers - comDrivers
        if i % numWorkers != processorID:
            continue
        process_group(gn, comDrivers)
    #
    if processorID == 0:
        gn = 'X'
        process_group(gn, xComDrivers)


def process_group(gn, comDrivers):
    ofpath = opath.join(dpath['communityProdDuration'], 'communityProdDuration-2009-%s.csv' % gn)
    with open(ofpath, 'wb') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['year', 'month', 'day', 'hour', 'did', 'pro-dur']
        writer.writerow(new_header)
    yy = '09'
    productive_state = ['dur%d' % x for x in [0, 3, 4, 5, 6, 7, 8, 9, 10]]
    shift_dpath, shift_prefix = '/home/sfcheng/toolbox/results', 'shift-hour-state-'
    for fn in os.listdir(shift_dpath):
        if not fnmatch(fn, '%s%s*.csv.gz' % (shift_prefix, yy)):
            continue
        fpath = '%s/%s' % (shift_dpath, fn)
        with gzip.open(fpath, 'rt') as r_csvfile:
            reader = csv.reader(r_csvfile)
            header = reader.next()
            hid = {h: i for i, h in enumerate(header)}
            for row in reader:
                did1 = int(row[hid['driver-id']])
                if did1 not in comDrivers:
                    continue
                month, day, hour = map(int, [row[hid[cn]] for cn in 'month day hour'.split()])
                cur_dtT = datetime(2009, month, day, hour)
                if cur_dtT.weekday() in [FRI, SAT, SUN]:
                    continue
                if (cur_dtT.year, cur_dtT.month, cur_dtT.day) in HOLIDAYS2009:
                    continue
                if cur_dtT.hour < AM10:
                    continue
                if PM8 <= cur_dtT.hour:
                    continue
                productive_duration = sum(int(row[hid[dur]]) for dur in productive_state)
                with open(ofpath, 'a') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow([row[hid['year']], row[hid['month']], row[hid['day']], hour,
                                     did1, productive_duration])


if __name__ == '__main__':
    run(0)

