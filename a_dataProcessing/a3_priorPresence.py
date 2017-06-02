import __init__
from init_project import *
#
from _utils.logger import get_logger
#
import os.path as opath


logger = get_logger()


def process_month(yymm):
    logger.info('handle the file; %s' % yymm)

    ofpath = '%s/%s%s.csv' % (of_dpath, of_prefixs, yymm)
    if opath.exists(ofpath):
        logger.info('The processed; %s' % yymm)
        return None


    ifpath = '%s/%s%s.csv' % (if_dpath, if_prefixs, yymm)
    if not check_path_exist(ifpath):
        logger.info('The file X exists; %s' % yymm)
        return None

    drivers = {}
    zones = generate_zones()
    handling_day = 0
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
                cur_dt = datetime.datetime.fromtimestamp(t)
                if handling_day != cur_dt.day:
                    logger.info('Processing %s %dth day (month %d)' % (yymm, cur_dt.day, cur_dt.month))
                    handling_day = cur_dt.day
                did = int(row[hid['did']])
                zi, zj = int(row[hid['zi']]), int(row[hid['zj']])
                try:
                    z = zones[(zi, zj)]
                except KeyError:
                    continue
                if not drivers.has_key(did):
                    drivers[did] = ca_driver_withPrevDrivers(did)
                prevDrivers = drivers[did].find_prevDriver(t, z)
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


class zone(object):
    def __init__(self, zi, zj):
        self.zi, self.zj = zi, zj
        self.logQ = []

    def add_driver_in_logQ(self, t, d):
        self.logQ.append([t, d])

    def update_logQ(self, t):
        while self.logQ and self.logQ[0][0] < t - HISTORY_LOOKUP_LENGTH:
            self.logQ.pop(0)

    def init_logQ(self):
        self.logQ = []


def generate_zones():
    zones = {}
    basic_zones = get_sg_zones()
    for k, z in basic_zones.iteritems():
        zones[k] = ca_zone(z.relation_with_poly, z.zi, z.zj, z.cCoor_gps, z.polyPoints_gps)
    return zones





if __name__ == '__main__':
    process_month('0901')