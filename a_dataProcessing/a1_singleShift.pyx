import __init__
from init_project import *
#
from _utils.logger import get_logger
#
import os.path as opath
import numpy as np
import gzip, csv
#

logger = get_logger()

def process_month(yymm):
    logger.info('handle the file; %s' % yymm)
    normal_fpath = opath.join(dpath['raw'], 'trips-%s-normal.csv.gz' % yymm)
    ext_fpath = opath.join(dpath['raw'], 'trips-%s-normal-ext.csv.gz' % yymm)
    if not opath.exists(normal_fpath):
        logger.info('The file X exists; %s' % yymm)
        return None
    ofpath = opath.join(dpath['singleShift'], 'singleShift-%s' % yymm)
    if opath.exists(ofpath + '.npy'):
        logger.info('Already handled; %s' % yymm)
        return None
    #
    vehicle_sharing = {}
    with gzip.open(normal_fpath, 'rt') as tripFileN:
        tripReaderN = csv.reader(tripFileN)
        tripHeaderN = tripReaderN.next()
        hidN = {h: i for i, h in enumerate(tripHeaderN)}
        with gzip.open(ext_fpath, 'rt') as tripHeaderE:
            tripReaderE = csv.reader(tripHeaderE)
            tripHeaderE = tripReaderE.next()
            hidE = {h: i for i, h in enumerate(tripHeaderE)}
            for rowN in tripReaderN:
                rowE = tripReaderE.next()
                did = int(rowE[hidE['driver-id']])
                if did == int('-1'):
                    continue
                vid = int(rowN[hidN['vehicle-id']])
                if not vehicle_sharing.has_key(vid):
                    vehicle_sharing[vid] = set()
                vehicle_sharing[vid].add(did)
    #
    ss_drivers = np.array([], dtype=int)
    for vid, drivers in vehicle_sharing.iteritems():
        if len(drivers) > 1:
            continue
        ss_drivers = np.append(ss_drivers, drivers.pop())
    np.save(ofpath, ss_drivers)
    logger.info('Filtering single-shift drivers; %s' % yymm)


if __name__ == '__main__':
    process_month('0901')