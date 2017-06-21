import __init__
from init_project import *
#
from d1_inputs import f_map_comStructure, f_map_netDemand, prefStrength, numSimRun
from d2_synTrajectory import gen_synTrajectories
from d3_individualTrajectory import split_trips
from d4_presenceBinary import convert_binRep
from d5_driverRelation import do_regression


def run(processorID, numWorkers=11):
    i = -1
    for sn in range(numSimRun + 21, numSimRun + 50):
        for ps in prefStrength:
            for cs in f_map_comStructure.iterkeys():
                for (ns, da) in f_map_netDemand:
                    i += 1
                    if i % numWorkers != processorID:
                        continue
                    # fn = 'synTrajectory-seed(%d)-ps(%.2f)-cs(%s)-ns(%s)-da(%s).csv' % (sn, ps, cs, ns, da)
                    # fpath = opath.join(dpath['synTrajectory'], fn)
                    # CS = f_map_comStructure[cs]()
                    # ODM = f_map_netDemand[(ns, da)]()
                    # gen_synTrajectories(fpath, sn, CS, ODM, ps)
                    # split_trips(sn, ps, cs, ns, da)
                    # convert_binRep(sn, ps, cs, ns, da)
                    # do_regression(sn, ps, cs, ns, da)
                    summary(sn, ps, cs, ns, da)



if __name__ == '__main__':
    run(0)