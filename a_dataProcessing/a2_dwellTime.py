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
    normal_fpath = opath.join(dpath['raw'], 'trips-%s-normal.csv.gz' % yymm)
    ext_fpath = opath.join(dpath['raw'], 'trips-%s-normal-ext.csv.gz' % yymm)
    log_fpath = opath.join(dpath['raw'], 'logs-%s-normal.csv.gz' % yymm)
    if not opath.exists(normal_fpath):
        logger.info('The file X exists; %s' % yymm)
        return None
    ss_drivers = set(np.load(opath.join(dpath['singleShift'], 'singleShift-%s.npy' % yymm), 'r+'))
    lons, lats = map(list, get_sgGrid())
    ofpath, handling_day = None, 0
    drivers = {}
    with gzip.open(normal_fpath, 'rt') as tripFileN:
        tripReaderN = csv.reader(tripFileN)
        tripHeaderN = tripReaderN.next()
        hidN = {h: i for i, h in enumerate(tripHeaderN)}
        with gzip.open(ext_fpath, 'rt') as tripHeaderE:
            tripReaderE = csv.reader(tripHeaderE)
            tripHeaderE = tripReaderE.next()
            hidE = {h: i for i, h in enumerate(tripHeaderE)}
            with gzip.open(log_fpath, 'rt') as logFile:
                logReader = csv.reader(logFile)
                logHeader = logReader.next()
                hidL = {h: i for i, h in enumerate(logHeader)}
                for rowN in tripReaderN:
                    rowE = tripReaderE.next()
                    #
                    did = int(rowE[hidE['driver-id']])
                    if did not in ss_drivers:
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
                    if handling_day != cur_dtT.day:
                        handling_day = cur_dtT.day
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
                    #
                    while True:
                        rowL = logReader.next()
                        logTime = eval(rowL[hidL['time']])
                        didL = int(rowL[hidL['driver-id']])
                        if didL not in ss_drivers:
                            continue
                        t = eval(rowL[hidL['time']])
                        cur_dtL = datetime.fromtimestamp(t)
                        if cur_dtL.weekday() in [FRI, SAT, SUN]:
                            continue
                        if (cur_dtT.year, cur_dtT.month, cur_dtT.day) in HOLIDAYS2009:
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

