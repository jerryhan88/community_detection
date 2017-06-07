import __init__
from init_project import *
#

import csv


def run():
    for fn in os.listdir(dpath['agtRecord']):
        if not fn.endswith('.csv'):
            continue
        process_file(fn)

def process_file(fn):
    _, _seedNum, _aid = fn[:-len('.csv')].split('-')
    ifpath = opath.join(dpath['agtRecord'], fn)
    prevAgents = set()
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            priorPresence = row[hid['prevAgents']]
            if not priorPresence:
                continue
            for _aid0 in priorPresence.split('|'):
                prevAgents.add(int(_aid0))
    prevAgents = list(prevAgents)
    prevAgents.sort()
    #
    ofpath = opath.join(dpath['agtPresence'], 'agtPresence-%s-%s.csv' % (_seedNum, _aid))
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['aid', 'zid', 'reward']
        new_header += prevAgents
        writer.writerow(new_header)
    #
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            new_row = [row[hid['aid']], row[hid['zid']], row[hid['reward']]]
            row_prevAgents = row[hid['prevAgents']]
            if not row_prevAgents:
                new_row += [0] * len(prevAgents)
            else:
                row_agents = map(int, row_prevAgents.split('|'))
                for aid in prevAgents:
                    if aid in row_agents:
                        new_row += [1]
                    else:
                        new_row += [0]
            with open(ofpath, 'a') as w_csvfile:
                writer = csv.writer(w_csvfile, lineterminator='\n')
                writer.writerow(new_row)


if __name__ == '__main__':
    run()