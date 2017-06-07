import __init__
from init_project import *
#
from _utils.logger import get_logger
#
from geopy.distance import vincenty
from math import sqrt
import csv


logger = get_logger()



def run():
    for fn in os.listdir(dpath['synData']):
        if not fn.endswith('.csv'):
            continue
        process_driver(fn)


def process_driver(fn):
    _, seedNum = fn[:-len('.csv')].split('-')
    with open(opath.join(dpath['synData'], fn), 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            aid = int(row[hid['aid']])
            ofpath = opath.join(dpath['agtRecord'], 'agtRecord-%s-%d.csv' % (seedNum, aid))
            if not opath.exists(ofpath):
                with open(ofpath, 'wt') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow(header)
            with open(ofpath, 'a') as w_csvfile:
                writer = csv.writer(w_csvfile, lineterminator='\n')
                writer.writerow(row)


if __name__ == '__main__':
    run()