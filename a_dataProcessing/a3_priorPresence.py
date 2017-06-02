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
    if check_path_exist(ofpath):
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


if __name__ == '__main__':
    process_month('0901')