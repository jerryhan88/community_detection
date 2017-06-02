import __init__
from init_project import *
#
from _utils.logger import get_logger
from _utils.geoFunctions import get_sgGrid
#
import os.path as opath
from datetime import datetime
from bisect import bisect
import numpy as np
import gzip, csv

logger = get_logger()


def process_month(yymm):
    logger.info('handle the file; %s' % yymm)
    normal_fpath = opath.join(dpath['raw'], 'trips-%s-normal.csv' % yymm)
    ext_fpath = opath.join(dpath['raw'], 'trips-%s-normal-ext.csv' % yymm)
    log_fpath = opath.join(dpath['raw'], 'logs-%s-normal.csv' % yymm)
    # normal_fpath = opath.join(dpath['raw'], 'trips-%s-normal.csv.gz' % yymm)
    # ext_fpath = opath.join(dpath['raw'], 'trips-%s-normal-ext.csv.gz' % yymm)
    # log_fpath = opath.join(dpath['raw'], 'logs-%s-normal.csv.gz' % yymm)
    if not opath.exists(normal_fpath):
        logger.info('The file X exists; %s' % yymm)
        return None
    ss_drivers = set(np.load(opath.join(dpath['singleShift'], 'singleShift-%s.npy' % yymm), 'r+'))
    lons, lats = map(list, get_sgGrid())
    ofpath, handling_dayT = None, 0
    handling_dayL = 0
    drivers = {}
    with open(normal_fpath, 'rb') as tripFileN:
    # with gzip.open(normal_fpath, 'rt') as tripFileN:
        tripReaderN = csv.reader(tripFileN)
        tripHeaderN = tripReaderN.next()
        hidN = {h: i for i, h in enumerate(tripHeaderN)}
        # with gzip.open(ext_fpath, 'rt') as tripHeaderE:
        with open(ext_fpath, 'rb') as tripHeaderE:
            tripReaderE = csv.reader(tripHeaderE)
            tripHeaderE = tripReaderE.next()
            hidE = {h: i for i, h in enumerate(tripHeaderE)}
            # with gzip.open(log_fpath, 'rt') as logFile:
            with open(log_fpath, 'rb') as logFile:
                logReader = csv.reader(logFile)
                logHeader = logReader.next()
                hidL = {h: i for i, h in enumerate(logHeader)}
                for rowN in tripReaderN:
                    rowE = tripReaderE.next()
                    #
                    didT = int(rowE[hidE['driver-id']])
                    if didT not in ss_drivers:
                        continue
                    #
                    tripTime = eval(rowN[hidN['start-time']])
                    cur_dtT = datetime.fromtimestamp(tripTime)
                    if cur_dtT.weekday() in [FRI, SAT, SUN]:
                        continue
                    if (cur_dtT.year, cur_dtT.month, cur_dtT.day) in HOLIDAYS2009:
                        continue
                    if cur_dtT.hour < AM10:
                        continue
                    if PM8 <= cur_dtT.hour:
                        continue
                    #
                    if handling_dayT != cur_dtT.day:
                        handling_dayT = cur_dtT.day
                        logger.info('Processing %s %dth day' % (yymm, cur_dtT.day))
                        ofpath = opath.join(dpath['dwellTime'],
                                            'dwellTime-%d%02d%02d.csv' % (cur_dtT.year, cur_dtT.month, cur_dtT.day))
                        with open(ofpath, 'wt') as w_csvfile:
                            writer = csv.writer(w_csvfile, lineterminator='\n')
                            writer.writerow(['year', 'month', 'day', 'hour',
                                             'time', 'lon', 'lat',
                                             'distance', 'duration', 'fare',
                                             'did',
                                             'zi', 'zj', 'dwellTime'])
                        drivers = {}
                    #
                    while True:
                        rowL = logReader.next()
                        logTime = eval(rowL[hidL['time']])
                        didL = int(rowL[hidL['driver-id']])
                        if didL not in ss_drivers:
                            continue
                        cur_dtL = datetime.fromtimestamp(logTime)
                        if handling_dayL != cur_dtL.day:
                            handling_dayL = cur_dtL.day
                            logger.info('\t Log processing %s %dth day' % (yymm, handling_dayL))
                        if cur_dtL.weekday() in [FRI, SAT, SUN]:
                            continue
                        if (cur_dtL.year, cur_dtL.month, cur_dtL.day) in HOLIDAYS2009:
                            continue
                        if cur_dtL.hour < AM10:
                            continue
                        if PM8 <= cur_dtL.hour:
                            continue
                        lon, lat = eval(rowL[hidL['longitude']]), eval(rowL[hidL['latitude']])
                        zi, zj = bisect(lons, lon) - 1, bisect(lats, lat) - 1
                        if zi < 0 or zj < 0:
                            continue
                        t, s = eval(rowL[hidL['time']]), eval(rowL[hidL['state']])
                        z = (zi, zj)
                        if not drivers.has_key(didL):
                            drivers[didL] = driver(didL, t, z, s)
                        else:
                            drivers[didL].update(t, z, s)
                        if tripTime <= logTime:
                            break
                    #
                    lon, lat = eval(rowN[hidN['start-long']]), eval(rowN[hidN['start-lat']])
                    zi, zj = bisect(lons, lon) - 1, bisect(lats, lat) - 1
                    if zi < 0 or zj < 0:
                        continue
                    if not drivers.has_key(didT):
                        continue
                    dwellTime = tripTime - drivers[didT].firstFreeStateTime \
                                if drivers[didT].firstFreeStateTime != -1 else 0
                    #
                    with open(ofpath, 'a') as w_csvfile:
                        writer = csv.writer(w_csvfile, lineterminator='\n')
                        writer.writerow([cur_dtT.year, cur_dtT.month, cur_dtT.day, cur_dtT.hour,
                                         tripTime, lon, lat,
                                         rowN[hidN['distance']], rowN[hidN['duration']], rowN[hidN['fare']],
                                         didT,
                                         zi, zj, dwellTime])


class driver(object):
    def __init__(self, did, cl_time, cl_zone, cl_state):
        self.did = did
        self.pl_time, self.pl_zone, self.pl_state = cl_time, cl_zone, cl_state
        if self.pl_state == FREE:
            self.firstFreeStateTime = self.pl_time
        else:
            self.firstFreeStateTime = -1

    def update(self, cl_time, cl_zone, cl_state):
        if cl_state != FREE:
            self.firstFreeStateTime = -1
        else:
            if self.pl_zone != cl_zone:
                self.firstFreeStateTime = cl_time
            else:
                if self.pl_state != FREE:
                    self.firstFreeStateTime = cl_time
        self.pl_time, self.pl_zone, self.pl_state = cl_time, cl_zone, cl_state


if __name__ == '__main__':
    process_month('0901')