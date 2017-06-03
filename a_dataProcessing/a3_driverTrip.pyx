import __init__
from init_project import *
#
from _utils.logger import get_logger
#
import threading
import time
import csv


logger = get_logger()
NUM_WORKERS = 11
locks_driverFile = {}


def run():
    whole_files = [[] for _ in xrange(NUM_WORKERS)]
    for i, fn in enumerate(os.listdir(dpath['dwellTimeNpriorPresence'])):
        if not fn.endswith('.csv'):
            continue
        whole_files[i % NUM_WORKERS] += [fn]
    for i, file_subset in enumerate(whole_files):
        t = threading.Thread(name='w%d' % i, target = process_files, args=(file_subset,))
        t.start()
        logger.info('thread w%d started' % i)

    logger.info('End the whole processes')


def process_files(fileNames):
    def append_row(fpath, row):
        locks_driverFile[did] = True
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow(row)
        locks_driverFile[did] = False
    #
    for fn in fileNames:
        _, yyyymmdd = fn[:-len('.csv')].split('-')
        logger.info('handling %s' % yyyymmdd)
        yyyy = yyyymmdd[:4]
        ifpath = opath.join(dpath['dwellTimeNpriorPresence'], fn)
        with open(ifpath, 'rb') as r_csvfile:
            reader = csv.reader(r_csvfile)
            header = reader.next()
            hid = {h: i for i, h in enumerate(header)}
            for row in reader:
                did = int(row[hid['did']])
                ofpath = opath.join(dpath['driverTrip'], 'driverTrip-%s-%d.csv' % (yyyy, did))
                if not locks_driverFile.has_key(did):
                    locks_driverFile[did] = True
                    with open(ofpath, 'wt') as w_csvfile:
                        writer = csv.writer(w_csvfile, lineterminator='\n')
                        writer.writerow(header)
                    locks_driverFile[did] = False
                if not locks_driverFile[did]:
                    append_row(ofpath, row)
                else:
                    while True:
                        time.sleep(1)
                        if not locks_driverFile[did]:
                            append_row(ofpath, row)
                            break


if __name__ == '__main__':
    run()