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
    ofpath = None
    for fn in os.listdir(dpath['dwellTimeNpriorPresence']):
        if not fn.endswith('.csv'):
            continue
        ifpath = opath.join(dpath['dwellTimeNpriorPresence'], fn)
        with open(ifpath, 'rb') as r_csvfile:
            reader = csv.reader(r_csvfile)
            header = reader.next()
            if not ofpath:
                ofpath = opath.join(dpath['communityTripWP'], 'communityTripWP-2009-%s.csv' % gn)
                with open(ofpath, 'wt') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    new_header = header[:-1]
                    writer.writerow(new_header)
            hid = {h: i for i, h in enumerate(header)}
            for row in reader:
                if int(row[hid['did']]) not in comDrivers:
                    continue
                new_row = row[:-1]
                with open(ofpath, 'a') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow(new_row)


if __name__ == '__main__':
    run(0)
