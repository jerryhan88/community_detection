import __init__
from init_project import *
#
logger = get_logger()


def run(processorID, numWorkers=11):
    for i, fn in enumerate(os.listdir(dpath['graphPartition'])):
        if i % numWorkers != processorID:
            continue
        if not fn.endswith('.pkl'):
            continue
        if 2 < len(fn.split('-')):
            continue
        _, gn = fn[:-len('.pkl')].split('-')
        if gn in ['original', 'drivers']:
            continue
        process_group(gn)


def process_group(gn):
    ifpath = opath.join(dpath['graphPartition'], 'graphPartition-%s.pkl' % gn)
    igG = ig.Graph.Read_Pickle(ifpath)
    comDrivers = set(v['name'] for v in igG.vs)
    ofpath = None
    for fn in os.listdir(dpath['dwellTimeNpriorPresence']):
        if not fn.endswith('.csv'):
            continue
        ifpath = opath.join(dpath['dwellTimeNpriorPresence'], fn)
        with open(ifpath, 'rb') as r_csvfile:
            reader = csv.reader(r_csvfile)
            header = reader.next()
            if not ofpath:
                ofpath = opath.join(dpath['communityTrip'], 'communityTrip-2009-%s.csv' % gn)
                with open(ofpath, 'wt') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    new_header = header[:-1]
                    new_header += list(comDrivers)
                    writer.writerow(new_header)
            hid = {h: i for i, h in enumerate(header)}
            for row in reader:
                if int(row[hid['did']]) not in comDrivers:
                    continue
                new_row = row[:-1]
                priorPresence = row[hid['priorPresence']]
                if not priorPresence:
                    new_row += [0] * len(comDrivers)
                else:
                    prevDrivers = set()
                    for did_lon_lat in priorPresence.split('|'):
                        _did, _, _ = did_lon_lat.split('&')
                        prevDrivers.add(int(_did))
                    for did0 in comDrivers:
                        if did0 in prevDrivers:
                            new_row += [1]
                        else:
                            new_row += [0]
                with open(ofpath, 'a') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow(new_row)


if __name__ == '__main__':
    run(0)

