import __init__
from init_project import *
#
from _utils.demand import od_matrix
from _utils.randx import ArbRand


def run(seedNum):
    seed(seedNum)
    #
    # Define a community structure and generate drivers
    #
    com_structure = [
        [1],
        [2, 3],
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
    Z = [x for x in xrange(5)]
    M = [
         [0, 0, 0, 1, 1],
         [0, 0, 0, 2, 1],
         [0, 0, 0, 1, 2],
         [0, 0, 1, 0, 0],
         [1, 1, 0, 0, 0]
         ]
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
    maxNumIter = 100
    numIter = 0
    while numIter < maxNumIter:
        print
        print '------------------------------------%d' % numIter
        print 'current driver position'
        for zid, z_drivers in zone_drivers.iteritems():
            print 'zid %d: %s' % (zid, str(z_drivers))
        print
        for d in drivers.itervalues():
            d.rd_info = []
        #
        unit_arrivals = ODM.get_unit_arrivals()
        print 'unit arrivals'
        for zid in Z:
            if not unit_arrivals.has_key(zid):
                unit_arrivals[zid] = []
            print 'zid %d: %s' % (zid, str(unit_arrivals[zid]))
        print
        l_drivers, n_drivers = set(), set()
        for zid, z_drivers in zone_drivers.iteritems():
            if unit_arrivals.has_key(zid):
                remaining_demand = len(unit_arrivals[zid]) - len(z_drivers)
                if remaining_demand > 0:
                    for d in z_drivers:
                        d.broadcast_info(zid, remaining_demand)
                        l_drivers.add(d)
                elif remaining_demand == 0:
                    for d in z_drivers:
                        n_drivers.add(d)
        f_drivers, s_drivers = set(), set()
        for d in drivers.itervalues():
            if d in l_drivers or d in n_drivers:
                continue
            if d.rd_info:
                f_drivers.add(d)
            else:
                s_drivers.add(d)
        for s_d in s_drivers:
            zid = s_d.z
            init_demand, init_supply = map(len, [unit_arrivals[zid], zone_drivers[zid]])
            if 0 <= init_demand - init_supply:
                dwellTime = 0
            else:
                total_arrival_rate = sum(M[zid])
                dwellTime = abs(init_demand - init_supply) / float(total_arrival_rate)
            prevDrivers = set([])
        #
        #
        #
        fol_maxD_zid = dict()
        zid_followers = {zid: set() for zid in Z}
        for f in f_drivers:
            f.rd_info.sort(key=lambda x: x[1], reverse=True)
            maxD_zid, _ = f.rd_info[0]
            zid_followers[maxD_zid].add(f)
            fol_maxD_zid[f] = maxD_zid
        #
        # calculate dwell time
        #
        profitableF, nonProfitableF = set(), set()
        for f, zid in fol_maxD_zid.iteritems():
            init_demand, init_supply, addi_supply = map(len,
                                                        [unit_arrivals[zid], zone_drivers[zid], zid_followers[zid]])
            last_demand = (init_demand - init_supply) - addi_supply
            if 0 <= last_demand:
                dwellTime = 0
                profitableF.add(f)
            else:
                total_arrival_rate = sum(M[zid])
                dwellTime = abs(last_demand) / float(total_arrival_rate)
                nonProfitableF.add(f)
            prevDrivers = set([d for d in zone_drivers[zid] if d in l_drivers or d in n_drivers])

        print 'l_drivers: %s' % str([str(d) for d in l_drivers])
        print 'n_drivers: %s' % str([str(d) for d in n_drivers])
        print 's_drivers: %s' % str([str(d) for d in s_drivers])
        print 'f_drivers: %s' % str([str(d) for d in f_drivers])
        print '\t\t profitableF: %s' % str([str(d) for d in profitableF])
        print '\t\t nonProfitableF: %s' % str([str(d) for d in nonProfitableF])
        print
        #
        # update positions
        #
        # print unit_arrivals
        for ln_d in list(l_drivers) + list(n_drivers):
            fz = ln_d.z
            zone_drivers[fz].remove(ln_d)
            #
            tz = unit_arrivals[fz].pop()
            zone_drivers[tz].add(ln_d)
            ln_d.set_zone(tz)

        for f_d in f_drivers:
            fz = f_d.z
            zone_drivers[fz].remove(f_d)
            #
            moved_zid = fol_maxD_zid[f_d]
            if f_d in profitableF:
                tz = unit_arrivals[moved_zid].pop()
            elif f_d in nonProfitableF:
                tz = OMs[moved_zid].get()
            else:
                assert False
            zone_drivers[tz].add(f_d)
            f_d.set_zone(tz)

        for s_d in s_drivers:
            fz =s_d.z
            zone_drivers[fz].remove(s_d)
            #
            tz = OMs[fz].get()
            zone_drivers[tz].add(s_d)
            s_d.set_zone(tz)

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


if __name__ == '__main__':
    run(0)