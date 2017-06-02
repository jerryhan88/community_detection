import __init__
from init_project import *
#
from _utils.logger import get_logger
from _utils.geoFunctions import get_sgGrid
#
from collections import deque
import os.path as opath
from datetime import datetime
from bisect import bisect
import numpy as np
import gzip, csv

logger = get_logger()


def process_month(yymm):
    from traceback import format_exc
    #
    try:
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
        drivers, zones = None, None
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
                            ofpath = opath.join(dpath['dwellTimeNpriorPresence'],
                                                'dwellTimeNpriorPresence-%d%02d%02d.csv' % (cur_dtT.year, cur_dtT.month, cur_dtT.day))
                            with open(ofpath, 'wt') as w_csvfile:
                                writer = csv.writer(w_csvfile, lineterminator='\n')
                                writer.writerow(['year', 'month', 'day', 'hour',
                                                 'time', 'lon', 'lat',
                                                 'distance', 'duration', 'fare',
                                                 'did',
                                                 'zi', 'zj', 'dwellTime', 'priorPresence'])
                            drivers, zones = {}, {}
                            for zi in xrange(len(lons)):
                                for zj in xrange(len(lats)):
                                    zones[zi, zj] = zone(zi, zj)
                        #
                        while True:
                            rowL = logReader.next()
                            logTime = eval(rowL[hidL['time']])
                            cur_dtL = datetime.fromtimestamp(logTime)
                            if handling_dayL != cur_dtL.day:
                                handling_dayL = cur_dtL.day
                                logger.info('\t Log processing %s %dth day' % (yymm, handling_dayL))
                            if not drivers and handling_dayL != handling_dayT:
                                continue
                            didL = int(rowL[hidL['driver-id']])
                            if didL not in ss_drivers:
                                continue
                            if cur_dtL.hour < AM10:
                                continue
                            if PM8 <= cur_dtL.hour:
                                continue
                            lon, lat = eval(rowL[hidL['longitude']]), eval(rowL[hidL['latitude']])
                            zi, zj = bisect(lons, lon) - 1, bisect(lats, lat) - 1
                            if zi < 0 or zj < 0:
                                continue
                            state = eval(rowL[hidL['state']])
                            if not drivers.has_key(didL):
                                drivers[didL] = driver(didL, logTime, zi, zj, state)
                            else:
                                drivers[didL].update(logTime, zi, zj, state)
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
                        prevDriverLonLat = drivers[didT].get_prevDriverLonLat(tripTime, lon, lat, zones[(zi, zj)])
                        #
                        with open(ofpath, 'a') as w_csvfile:
                            writer = csv.writer(w_csvfile, lineterminator='\n')
                            new_row = [cur_dtT.year, cur_dtT.month, cur_dtT.day, cur_dtT.hour,
                                       tripTime, lon, lat,
                                       rowN[hidN['distance']], rowN[hidN['duration']], rowN[hidN['fare']],
                                       didT,
                                       zi, zj, dwellTime]
                            writer.writerow(new_row + ['|'.join(prevDriverLonLat)])
    except Exception as _:
        import sys
        with open('%s_%s.txt' % (sys.argv[0], yymm), 'w') as f:
            f.write(format_exc())
        raise


class driver(object):
    def __init__(self, did, cl_time, cl_zi, cl_zj, cl_state):
        self.did = did
        self.pl_time, self.pl_zi, self.pl_zj, self.pl_state = cl_time, cl_zi, cl_zj, cl_state
        if self.pl_state == FREE:
            self.firstFreeStateTime = self.pl_time
        else:
            self.firstFreeStateTime = -1
        #
        self.zoneEnteredTime = {}
        self.zoneEnteredTime[self.pl_zi, self.pl_zj] = self.pl_time

    def update(self, cl_time, cl_zi, cl_zj, cl_state):
        if (self.pl_zi, self.pl_zj) != (cl_zi, cl_zj):
            self.zoneEnteredTime[cl_zi, cl_zj] = cl_time
        #
        if cl_state != FREE:
            self.firstFreeStateTime = -1
        else:
            if (self.pl_zi, self.pl_zj) != (cl_zi, cl_zj):
                self.firstFreeStateTime = cl_time
            else:
                if self.pl_state != FREE:
                    self.firstFreeStateTime = cl_time
        self.pl_time, self.pl_zi, self.pl_zj, self.pl_state = cl_time, cl_zi, cl_zj, cl_state

    def get_prevDriverLonLat(self, pickUpTime, lon, lat, z):
        z.update_logQ(pickUpTime)
        if not self.zoneEnteredTime.has_key((z.zi, z.zj)):
            did1_zEnteredTime = pickUpTime
        else:
            did1_zEnteredTime = self.zoneEnteredTime[z.zi, z.zj]
        prevDriverLonLat = {}
        for _, d, lon, lat in z.logQ:
            if d.did == self.did:
                continue
            if d.zoneEnteredTime.has_key((z.zi, z.zj)):
                did0_zEnteredTime = d.zoneEnteredTime[z.zi, z.zj]
                if did0_zEnteredTime < did1_zEnteredTime:
                    prevDriverLonLat[d.did] = '%d&%f&%f' % (d.did, lon, lat)
            else:
                prevDriverLonLat[d.did] = '%d&%f&%f' % (d.did, lon, lat)
        z.add_driver_in_logQ(pickUpTime, self, lon, lat)
        return prevDriverLonLat.values()


class zone(object):
    def __init__(self, zi, zj):
        self.zi, self.zj = zi, zj
        self.logQ = deque()

    def add_driver_in_logQ(self, pickUpTime, d, lon, lat):
        self.logQ += [[pickUpTime, d, lon, lat]]

    def update_logQ(self, pickUpTime):
        while self.logQ and self.logQ[0][0] < pickUpTime - HISTORY_LOOKUP_LENGTH:
            self.logQ.popleft()


if __name__ == '__main__':
    process_month('0901')