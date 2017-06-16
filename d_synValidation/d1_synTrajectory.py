import __init__
from init_project import *
#
from _utils.demand import od_matrix
from _utils.randx import ArbRand


DISPLAY_LOG = False


def run(seedNum):
    def append_record(fpath, numIter, did, zid, dwellTime, prevDrivers):
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([numIter, did, zid, dwellTime, '|'.join(['%d' % d.did for d in prevDrivers])])
    #
    seed(seedNum)
    fpath = opath.join(dpath['synTrajectory'], 'synTrajectory-%d.csv' % seedNum)
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = ['iterNum', 'did', 'z', 'DT', 'prevDrivers']
        writer.writerow(header)
    #
    # Define a community structure and generate drivers
    #
    com_structure = [
        [1],
        [2], [3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12]
    ]
    drivers = {did: driver(did) for did in chain(*com_structure)}
    for cid, c_members in enumerate(com_structure):
        for did in c_members:
            drivers[did].set_community(cid, [drivers[c_did] for c_did in set(c_members) - {did}])
    #
    # Define a OD matrix which represents arrival rates
    #

    # M = [
    #      [0, 0, 0, 1, 1],
    #      [0, 0, 0, 2, 1],
    #      [0, 0, 0, 1, 2],
    #      [0, 0, 1, 0, 0],
    #      [1, 1, 0, 0, 0]
    #      ]

    M = [
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 0, 1, 0, 0, 0, 0, 0]
    ]

    # M = gen_M(20, 0.35)

    Z = [x for x in xrange(len(M))]



    ODM = od_matrix(Z, M)
    OMs = {}
    for i in xrange(len(M)):
        OMs[i] = ArbRand([M[i][j]/ float(sum(M[i])) for j in xrange(len(M[i]))])
    #
    # Initialize drivers' position
    #
    zone_drivers = {zid: set() for zid in Z}
    for d in drivers.itervalues():
        z = choice(Z)
        zone_drivers[z].add(d)
        d.set_zone(z)
    #
    # Run simulation
    #
    maxNumIter = 10000
    numIter = 0
    while numIter < maxNumIter:

        for d in drivers.itervalues():
            d.rd_info = []
        #
        p_z = ODM.get_unit_arrivals()
        for z in Z:
            if not p_z.has_key(z):
                p_z[z] = []
        #
        leaders, fortunateDrivers = set(), set()
        for z, z_drivers in zone_drivers.iteritems():
            if p_z.has_key(z):
                remaining_demand = len(p_z[z]) - len(z_drivers)
                if remaining_demand > 0:
                    for d in z_drivers:
                        d.broadcast_info(z, remaining_demand)
                        leaders.add(d)
                elif remaining_demand == 0:
                    for d in z_drivers:
                        fortunateDrivers.add(d)
        followers, unfortunateDrivers = set(), set()
        for d in drivers.itervalues():
            if d in leaders or d in fortunateDrivers:
                continue
            if d.rd_info:
                followers.add(d)
            else:
                unfortunateDrivers.add(d)
        for uft_d in unfortunateDrivers:
            z = uft_d.z
            Dz, Sz = map(len, [p_z[z], zone_drivers[z]])
            assert Dz - Sz < 0
            total_arrival_rate = sum(M[z])
            DT = abs(Dz - Sz) / float(total_arrival_rate)
            prevDrivers = set([])
            append_record(fpath, numIter, uft_d.did, z, DT, prevDrivers)
        #
        # choose the zone whose remaining demand is the highest
        #
        fol_maxD_zid = dict()
        zid_followers = {zid: set() for zid in Z}
        for f_d in followers:
            f_d.rd_info.sort(key=lambda x: x[1], reverse=True)
            maxD_zid, _ = f_d.rd_info[0]
            zid_followers[maxD_zid].add(f_d)
            fol_maxD_zid[f_d] = maxD_zid
        #
        # calculate dwell time
        #
        profitableF, nonProfitableF = set(), set()
        for f_d, z in fol_maxD_zid.iteritems():
            Dz, Sz, Fz = map(len, [p_z[z], zone_drivers[z], zid_followers[z]])
            last_demand = (Dz - Sz) - Fz
            if 0 <= last_demand:
                DT = 0
                profitableF.add(f_d)
            else:
                total_arrival_rate = sum(M[z])
                DT = abs(last_demand) / float(total_arrival_rate)
                nonProfitableF.add(f_d)
            prevDrivers = set([d for d in zone_drivers[z] if d in leaders or d in fortunateDrivers])
            append_record(fpath, numIter, f_d.did, z, DT, prevDrivers)
        #
        if DISPLAY_LOG:
            print
            print '------------------------------------%d' % numIter
            print 'current driver position'
            for z, z_drivers in zone_drivers.iteritems():
                print 'z %d: %s' % (z, str(z_drivers))
            print
            print 'unit arrivals'
            for z in Z:
                print 'z %d: %s' % (z, str(p_z[z]))
            print
            print 'leaders: %s' % str([str(d) for d in leaders])
            print 'fortunateDrivers: %s' % str([str(d) for d in fortunateDrivers])
            print 'unfortunateDrivers: %s' % str([str(d) for d in unfortunateDrivers])
            print 'followers: %s' % str([str(d) for d in followers])
            print '\t\t profitableF: %s' % str([str(d) for d in profitableF])
            print '\t\t nonProfitableF: %s' % str([str(d) for d in nonProfitableF])
            print
        #
        # update positions
        #
        for ln_d in list(leaders) + list(fortunateDrivers):
            fz = ln_d.z
            zone_drivers[fz].remove(ln_d)
            #
            tz = p_z[fz].pop()
            zone_drivers[tz].add(ln_d)
            ln_d.set_zone(tz)
        #
        for f_d in followers:
            fz = f_d.z
            zone_drivers[fz].remove(f_d)
            #
            moved_zid = fol_maxD_zid[f_d]
            if f_d in profitableF:
                tz = p_z[moved_zid].pop()
            elif f_d in nonProfitableF:
                tz = OMs[moved_zid].get()
            else:
                assert False
            zone_drivers[tz].add(f_d)
            f_d.set_zone(tz)
        #
        for uft_d in unfortunateDrivers:
            fz =uft_d.z
            zone_drivers[fz].remove(uft_d)
            #
            tz = OMs[fz].get()
            zone_drivers[tz].add(uft_d)
            uft_d.set_zone(tz)
        #
        numIter += 1


class driver(object):
    def __init__(self, did):
        self.did = did

    def __repr__(self):
        return 'did%d(c%d)' % (self.did, self.cid)

    def set_community(self, cid, c_members):
        self.cid, self.c_members = cid, c_members

    def set_zone(self, z):
        self.z = z

    def broadcast_info(self, zid, rd):
        for d in self.c_members:
            d.rd_info += [(zid, rd)]


def gen_M(numZones, p):
    M = [[0] * numZones for _ in xrange(numZones)]
    for i in xrange(numZones):
        for j in xrange(numZones):
            if i == j:
                continue
            if random() < p:
                M[i][j] = randint(0, 3)
    return M


if __name__ == '__main__':
    run(3)