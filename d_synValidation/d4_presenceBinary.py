import __init__
from init_project import *
#


def convert_binRep(sn, ps, cs, ns, da):
    regExp = 'individualTrajectory-seed(%d)-ps(%.2f)-cs(%s)-ns(%s)-da(%s)-*.csv' % (sn, ps, cs, ns, da)
    for fn in os.listdir(dpath['individualTrajectory']):
        if not fnmatch(fn, regExp):
            continue
        ifpath = opath.join(dpath['individualTrajectory'], fn)
        prevDrivers = set()
        with open(ifpath, 'rb') as r_csvfile:
            reader = csv.reader(r_csvfile)
            header = reader.next()
            hid = {h: i for i, h in enumerate(header)}
            for row in reader:
                priorPresence = row[hid['PD']]
                if not priorPresence:
                    continue
                for _did0 in priorPresence.split('|'):
                    prevDrivers.add(int(_did0))
        prevDrivers = list(prevDrivers)
        prevDrivers.sort()
        #
        ofpath = opath.join(dpath['presenceBinary'], fn.replace('individualTrajectory', 'presenceBinary'))
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
                new_row = [row[hid[cn]] for cn in 'did z DT'.split()]
                row_prevDrivers = row[hid['PD']]
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
    run(2)