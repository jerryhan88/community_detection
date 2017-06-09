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
    ofpath = opath.join(dpath['communityTrip'], 'communityTrip-2009-%s.csv' % gn)
    for fn in os.listdir(dpath['dwellTimeNpriorPresence']):
        if not fn.endswith('.csv'):
            continue
        ifpath = opath.join(dpath['dwellTimeNpriorPresence'], fn)
        with open(ifpath, 'rb') as r_csvfile:
            reader = csv.reader(r_csvfile)
            header = reader.next()
            with open(ofpath, 'wt') as w_csvfile:
                writer = csv.writer(w_csvfile, lineterminator='\n')
                writer.writerow(header)
            hid = {h: i for i, h in enumerate(header)}
            for row in reader:
                if int(row[hid['did']]) not in comDrivers:
                    continue
                with open(ofpath, 'a') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow(row)



if __name__ == '__main__':
    run(0)

