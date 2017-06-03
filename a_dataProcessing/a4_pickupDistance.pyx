import __init__
from init_project import *
#
from _utils.logger import get_logger
#
from geopy.distance import vincenty
from math import sqrt
import csv


logger = get_logger()

NUM_WORKERS = 11
MAX_DIST = ZONE_UNIT_KM * sqrt(2)


def run(processorID):
    for i, fn in enumerate(os.listdir(dpath['driverTrip'])):
        if not fn.endswith('.csv'):
            continue
        if i % NUM_WORKERS != processorID:
            continue
        process_driver(fn)


def process_driver(fn):
    logger.info('handling %s' % fn)
    prevDrivers = set()
    ifpath = opath.join(dpath['driverTrip'], fn)
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            priorPresence = row[hid['priorPresence']]
            if not priorPresence:
                continue
            for did_lon_lat in priorPresence.split('|'):
                _did, _, _ = did_lon_lat.split('&')
                prevDrivers.add(int(_did))
    prevDrivers = list(prevDrivers)
    prevDrivers.sort()
    #
    _, yyyy, did = fn[:-len('.csv')].split('-')
    ofpath = opath.join(dpath['pickupDistance'], 'pickupDistance-%s-%s.csv' % (yyyy, did))
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['year', 'month', 'day', 'hour',
                         'time', 'lon', 'lat',
                         'distance', 'duration', 'fare',
                         'did',
                         'zi', 'zj', 'dwellTime']
        new_header += prevDrivers
        writer.writerow(new_header)
    #
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            new_row = row[:-1]
            priorPresence = row[hid['priorPresence']]
            if not priorPresence:
                new_row += [0] * len(prevDrivers)
            else:
                did1_lon, did1_lat = map(eval, [row[hid[cn]] for cn in 'lon lat'.split()])
                #
                did0_pickLoc = {}
                for did_lon_lat in priorPresence.split('|'):
                    _did, _lon, _lat = did_lon_lat.split('&')
                    did0_pickLoc[int(_did)] = map(eval, [_lon, _lat])
                for did0 in prevDrivers:
                    if did0_pickLoc.has_key(did0):
                        did0_lon, did0_lat = did0_pickLoc[did0]
                        dist = vincenty((did1_lon, did1_lat), (did0_lon, did0_lat)).kilometers
                        new_row += [1 - dist / MAX_DIST]
                    else:
                        new_row += [0]
            with open(ofpath, 'a') as w_csvfile:
                writer = csv.writer(w_csvfile, lineterminator='\n')
                writer.writerow(new_row)
    logger.info('end %s' % fn)


if __name__ == '__main__':
    run(0)