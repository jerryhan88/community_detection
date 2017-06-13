import __init__
from init_project import *
#


def run(seedNum):
    for fn in os.listdir(dpath['individualTrajectory']):
        if not fnmatch(fn, '*-%d-*.csv' % seedNum):
            continue
        process_file(fn)

def process_file(fn):
    _, _seedNum, _aid = fn[:-len('.csv')].split('-')
    ifpath = opath.join(dpath['individualTrajectory'], fn)
    prevDrivers = set()
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            priorPresence = row[hid['prevDrivers']]
            if not priorPresence:
                continue
            for _did0 in priorPresence.split('|'):
                prevDrivers.add(int(_did0))
    prevDrivers = list(prevDrivers)
    prevDrivers.sort()
    #
    ofpath = opath.join(dpath['presenceBinary'], 'presenceBinary-%s-%s.csv' % (_seedNum, _aid))
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['did', 'zid', 'dwellTime']
        new_header += prevDrivers
        writer.writerow(new_header)
    #
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            new_row = [row[hid[cn]] for cn in 'did zid dwellTime'.split()]
            row_prevDrivers = row[hid['prevDrivers']]
            if not row_prevDrivers:
                new_row += [0] * len(prevDrivers)
            else:
                row_agents = map(int, row_prevDrivers.split('|'))
                for did in prevDrivers:
                    if did in row_agents:
                        new_row += [1]
                    else:
                        new_row += [0]
            with open(ofpath, 'a') as w_csvfile:
                writer = csv.writer(w_csvfile, lineterminator='\n')
                writer.writerow(new_row)


if __name__ == '__main__':
    run(5)