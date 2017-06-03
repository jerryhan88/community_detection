import __init__
from init_project import *
#


from _utils.logger import get_logger


logger = get_logger()
NUM_WORKERS = 11



def run(processorID):
    for i, fn in enumerate(os.listdir(dpath['dwellTimeNpriorPresence'])):
        if not fn.endswith('.csv'):
            continue
        if i % NUM_WORKERS != processorID:
            continue
        process_driver(fn)


def process_driver(fn):

    pass