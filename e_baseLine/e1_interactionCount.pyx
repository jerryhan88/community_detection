import __init__
from init_project import *
#
from _utils.logger import get_logger
#

logger = get_logger()

HOUR1 = 3600


def run(processorID, numWorkers=11):
    for i, fn in enumerate(os.listdir(dpath['pickupDistance'])):
        if not fn.endswith('.csv'):
            continue
        if i % numWorkers != processorID:
            continue
        process_driver(fn)


def process_driver(fn):
    logger.info('handling %s' % fn)
    try:
        _, yyyy, _did1 = fn[:-len('.csv')].split('-')
        ofpath = opath.join(dpath['interactionCount'], 'interactionCount-%s-%s.pkl' % (yyyy, _did1))
        if opath.exists(ofpath):
            return None
        ifpath = opath.join(dpath['pickupDistance'], fn)
        df = pd.read_csv(ifpath)
        df = df[(df['dwellTime'] != 0) & (df['dwellTime'] < HOUR1)]
        cns = 'year month day hour time lon lat distance duration fare did zi zj dwellTime'.split()
        prevDrivers = [cn for cn in df.columns if cn not in cns]
        relationCount = {int(_did0): len(df[(df[_did0] != 0)]) for _did0 in prevDrivers}
        #
        with open(ofpath, 'wb') as fp:
            pickle.dump([len(df), relationCount], fp)
    except Exception as _:
        import sys
        with open('%s_%s.txt' % (sys.argv[0], fn), 'w') as f:
            f.write(format_exc())
        raise
    logger.info('end %s' % fn)


if __name__ == '__main__':
    # run(1)
    process_driver('pickupDistance-2009-13959.csv')