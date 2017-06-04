import __init__
from init_project import *
#
import pandas as pd
import csv


NUM_WORKERS = 11

def run(processorID):
    for i, fn in enumerate(os.listdir(dpath['pickupDistance'])):
        if not fn.endswith('.csv'):
            continue
        if i % NUM_WORKERS != processorID:
            continue
        process_driver(fn)

def process_driver(fn):
    ifpath = opath.join(dpath['pickupDistance'], fn)
    df = pd.read_csv(ifpath)
    numWholeRecords = len(df)
    _, yyyy, _did1 = fn[:-len('.csv')].split('-')
    ofpath = opath.join(dpath['individualCounting'], 'individualCounting-%s-%s.csv' % (yyyy, _did1))
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = ['did1', 'numWholeRecords',
                  'did0', 'numEncounters']
        writer.writerow(header)
    cns = 'year month day hour time lon lat distance duration fare did zi zj dwellTime'.split()
    prevDrivers = [cn for cn in df.columns if cn not in cns]
    for _did0 in prevDrivers:
        num_encouters = sum([1 for v in df[_did0] if v !=0])
        with open(ofpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [_did1, numWholeRecords,
                       _did0, num_encouters]
            writer.writerow(new_row)

if __name__ == '__main__':
    run(2)