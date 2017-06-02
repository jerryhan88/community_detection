import __init__
from init_project import *
#
from _utils.logger import get_logger
#
from collections import deque
import os.path as opath
import os
import csv

logger = get_logger()

NUM_PROCESSORS = 11


def run(processorID):
    for i, fn in enumerate(os.listdir(dpath['dwellTime'])):
        if not fn.startswith('dwellTime'):
            continue
        if i % NUM_PROCESSORS != processorID:
            continue
        _, yyyymmdd = fn[:-len('.csv')].split('-')
        process_day(yyyymmdd)



class zone(object):
    def __init__(self, zi, zj):
        self.zi, self.zj = zi, zj
        self.logQ = deque()

    def add_driver_in_logQ(self, t, d):
        self.logQ.append([t, d])

    def update_logQ(self, t):
        while self.logQ and self.logQ[0][0] < t - HISTORY_LOOKUP_LENGTH:
            self.logQ.dq.popleft()




def process_day(yyyymmdd):
    logger.info('handle the file; %s' % yyyymmdd)
    ofpath = opath.join(dpath['priorPresence'], 'priorPresence-%s.csv' % yyyymmdd)
    if opath.exists(ofpath):
        logger.info('The processed; %s' % yyyymmdd)
        return None
    ifpath = opath.join(dpath['dwellTime'], 'dwellTime-%s.csv' % yyyymmdd)

    zones = generate_zones()
    drivers = {}
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        with open(ofpath, 'wt') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_header = header + ['prevDrivers']
            writer.writerow(new_header)
            for row in reader:
                t = eval(row[hid['time']])
                did = int(row[hid['did']])
                zi, zj = int(row[hid['zi']]), int(row[hid['zj']])
                try:
                    z = zones[(zi, zj)]
                except KeyError:
                    continue
                if not drivers.has_key(did):
                    drivers[did] = driver(did)
                prevDrivers = drivers[did].get_prevDriverLonLat(t, z)
                writer.writerow(row + ['&'.join(map(str, prevDrivers))])


class driver(object):
    def __init__(self, did):
        self.did = did

    def find_prevDriver(self, t, z):
        z.update_logQ(t)
        prevDrivers = set()
        for _, d in z.logQ:
            if d.did == self.did:
                continue
            prevDrivers.add(d.did)
        z.add_driver_in_logQ(t, self)
        return prevDrivers







if __name__ == '__main__':
    process_month('0901')