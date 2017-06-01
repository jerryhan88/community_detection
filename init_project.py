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
dpath['dwellTime'] = opath.join(dpath['home'], 'dwellTime')


for dn in ['home', 'singleShift', 'dwellTime']:
    try:
        if not opath.exists(dpath[dn]):
            os.makedirs(dpath[dn])
    except OSError:
        pass

# ss_drivers_dpath, ss_drivers_prefix = '%s/%s' % (tc_data, 'ss_drivers_by_trip'), 'ss-drivers-'