import __init__
from init_project import *
#
from _utils.logger import get_logger
#

logger = get_logger()


def split_trips(sn, ps, cs, ns, da):
    fn = 'synTrajectory-seed(%d)-ps(%.2f)-cs(%s)-ns(%s)-da(%s).csv' % (sn, ps, cs, ns, da)
    ifpath = opath.join(dpath['synTrajectory'], fn)
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            did = int(row[hid['did']])
            fn = 'individualTrajectory-seed(%d)-ps(%.2f)-cs(%s)-ns(%s)-da(%s)-did(%d).csv' % (sn, ps, cs, ns, da, did)
            ofpath = opath.join(dpath['individualTrajectory'], fn)
            if not opath.exists(ofpath):
                with open(ofpath, 'wt') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow(header)
            with open(ofpath, 'a') as w_csvfile:
                writer = csv.writer(w_csvfile, lineterminator='\n')
                writer.writerow(row)


if __name__ == '__main__':
    pass