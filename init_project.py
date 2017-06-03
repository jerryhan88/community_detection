import os.path as opath
import os
dpath = {}
taxi_data_home = opath.join(opath.join(opath.dirname(opath.realpath(__file__)), '..'), 'taxi_data')
dpath['raw'] = opath.join(taxi_data_home, 'raw')
dpath['geo'] = opath.join(taxi_data_home, 'geo')
ZONE_UNIT_KM = 0.5
# --------------------------------------------------------------
dpath['home'] = opath.join(taxi_data_home, 'communityDetection')
dpath['singleShift'] = opath.join(dpath['home'], 'singleShift')
dpath['dwellTimeNpriorPresence'] = opath.join(dpath['home'], 'dwellTimeNpriorPresence')
dpath['driverTrip'] = opath.join(dpath['home'], 'driverTrip')
dpath['pickupDistance'] = opath.join(dpath['home'], 'pickupDistance')
dpath['individualRelation'] = opath.join(dpath['home'], 'individualRelation')

for dn in ['home', 'singleShift',
           'dwellTimeNpriorPresence', 'driverTrip', 'pickupDistance',
           'individualRelation']:
    try:
        if not opath.exists(dpath[dn]):
            os.makedirs(dpath[dn])
    except OSError:
        pass

MON, TUE, WED, THR, FRI, SAT, SUN = range(7)
AM10, PM8 = 10, 20
# Singapore Public Holidays
HOLIDAYS2009 = [
            (2009, 1, 1),    # New Year's Day, Thursday, 1 January 2009
            (2009, 1, 26),    # Chinese New Year, Monday, 26 January 2009
            (2009, 1, 27),    # Chinese New Year, Tuesday, 27 January 2009
            (2009, 4, 10),    # Good Friday, Friday, 10 April 2009
            (2009, 5, 1),     # Labour Day, Friday, 1 May 2009
            (2009, 5, 9),     # Vesak Day, Saturday, 9 May 2009
            (2009, 8, 10),    # National Day, Sunday*, 9 August 2009
            (2009, 9, 21),    # Hari Raya Puasa, Sunday*, 20 September 2009
            (2009, 11, 16),   # Deepavali, Sunday*, 15 November 2009
            (2009, 11, 27),   # Hari Raya Haji, Friday, 27 November 2009
            (2009, 12, 25),   # Christmas Day, Friday, 25 December 2009
]
FREE, POB = 0, 5
HISTORY_LOOKUP_LENGTH = 30 * 60
SIGINIFICANCE_LEVEL = 0.01
MIN_PICKUP_RATIO = 0.1