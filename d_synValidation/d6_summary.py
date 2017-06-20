import __init__
from init_project import *

from d1_inputs import f_map_comStructure, f_map_netDemand, prefStrength, numSimRun

def run():
    for ps in prefStrength:
        for cs in f_map_comStructure.iterkeys():
            for (ns, da) in f_map_netDemand:
                ofpath = opath.join(dpath['relationSummary'],
                                    'relationSummary-ps(%.2f)-cs(%s)-ns(%s)-da(%s).csv' % (ps, cs, ns, da))
                with open(ofpath, 'wt') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    header = ['seedNum', 'numRel',
                              'numMissingRel', 'numWrongRel', 'numPosRel',
                              'missingRel', 'wrongRel', 'posRel']
                    writer.writerow(header)
                process_instances(ofpath, ps, cs, ns, da)


def process_instances(ofpath, ps, cs, ns, da):
    regExp = 'driverRelation-*-ps(%.2f)-cs(%s)-ns(%s)-da(%s)-*.csv' % (ps, cs, ns, da)

    CS = f_map_comStructure[cs]()
    relationPairs = set()
    for c_members in CS:
        for d0 in c_members:
            for d1 in c_members:
                if d0 == d1:
                    continue
                relationPairs.add((d0, d1))

    seedNum_files = {}
    for fn in os.listdir(dpath['driverRelation']):
        if not fnmatch(fn, regExp):
            continue
        _, seedNum, _, _, _, _, _ = fn[:-len('.csv')].split('-')
        if not seedNum_files.has_key(seedNum):
            seedNum_files[seedNum] = []
        seedNum_files[seedNum] += [opath.join(dpath['driverRelation'], fn)]

    for seedNum, files in seedNum_files.iteritems():
        negRelation, posRelation = set(), set()
        for ifpath in files:
            with open(ifpath, 'rb') as r_csvfile:
                reader = csv.reader(r_csvfile)
                header = reader.next()
                hid = {h: i for i, h in enumerate(header)}
                for row in reader:
                    did1 = int(row[hid['did']])
                    _sigNegRelation = row[hid['sigNegRelation']]
                    if _sigNegRelation:
                        sigNegRelation = map(int, _sigNegRelation.split('|'))
                        for did0 in sigNegRelation:
                            negRelation.add((did0, did1))
                    _sigPosRelation = row[hid['sigPosRelation']]
                    if _sigPosRelation:
                        sigPosRelation = map(int, _sigPosRelation.split('|'))
                        for did0 in sigPosRelation:
                            posRelation.add((did0, did1))
        missingRel = relationPairs - negRelation
        wrongRel = negRelation - relationPairs
        with open(ofpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [seedNum, len(relationPairs),
                       len(missingRel), len(wrongRel), len(posRelation),
                       list(missingRel), list(wrongRel), list(posRelation)]
            writer.writerow(new_row)


if __name__ == '__main__':
    run()