import __init__
from init_project import *
#
from _utils.demand import od_matrix
from _utils.randx import ArbRand


DISPLAY_LOG = False


def gen_synTrajectories(fpath, seedNum, CS, ODM, pStrength, maxIterNum=5000):
    def append_record(fpath, numIter, did, zid, dwellTime, prevDrivers):
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([numIter, did, zid, dwellTime, '|'.join(['%d' % d.did for d in prevDrivers])])
    #
    seed(seedNum)
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = ['iterNum', 'did', 'z', 'DT', 'PD']
        writer.writerow(header)
    D = {did: driver(did) for did in chain(*CS)}
    for cid, c_members in enumerate(CS):
        for did in c_members:
            D[did].set_community(cid, [D[c_did] for c_did in set(c_members) - {did}])
    Z = [x for x in xrange(len(ODM))]
    demandGentor = od_matrix(Z, ODM)
    Bz = {}
    for i in xrange(len(ODM)):
        Bz[i] = ArbRand([ODM[i][j] / float(sum(ODM[i])) for j in xrange(len(ODM[i]))])
    #
    # Initialize D' position
    #
    Dz = {zid: set() for zid in Z}
    ld = {}
    for d in D.itervalues():
        zid = choice(Z)
        Dz[zid].add(d)
        ld[d] = zid
    #
    # Run simulation
    #
    iterNum = 0
    while iterNum < maxIterNum:
        Zd, gd = dict(), dict()
        for d in D.itervalues():
            Zd[d] = set(); gd[d] = None
        #
        gendD = demandGentor.get_unit_arrivals()
        nz = {}
        for zid in Z:
            nz[zid] = len(gendD[zid]) if gendD.has_key(zid) else 0
        #
        L, FD = set(), set()
        for d0 in D.itervalues():
            dsGAP = nz[ld[d0]] - len(Dz[ld[d0]])
            d0.update_memory(ld[d], dsGAP)
            if dsGAP > 0:
                for d1 in d0.Cd:
                    Zd[d1].add(ld[d0])
                L.add(d0)
            elif dsGAP == 0:
                FD.add(d0)
        F = set([d for d in D.itervalues() if Zd[d] and d not in L and d not in FD])
        UD = set(D.values()) - L - FD - F
        #
        Fz = {zid: set() for zid in Z}
        for d in UD:
            if random() < pStrength:
                max_dsGAP, max_id = -1e400, None
                for zid, dsGAP in d.dsGAP_memory.iteritems():
                    if zid == ld[d]:
                        continue
                    if max_dsGAP < dsGAP:
                        max_dsGAP = dsGAP
                        max_id = zid
                if max_id != None:
                    Fz[max_id].add(d)
                    gd[d] = max_id
        for d in F:
            max_dsGAP, max_id = -1e400, None
            for zid in Zd[d]:
                if max_dsGAP < (nz[zid] - len(Dz[zid])):
                    max_dsGAP = nz[zid] - len(Dz[zid])
                    max_id = zid
            if random() < pStrength:
                for zid, dsGAP in d.dsGAP_memory.iteritems():
                    if zid == ld[d]:
                        continue
                    if max_dsGAP < dsGAP:
                        max_dsGAP = dsGAP
                        max_id = zid
            assert max_id != None
            Fz[max_id].add(d)
            gd[d] = max_id

        for d in list(UD) + list(F):
            if gd[d] == None:
                assert d not in F
                assert nz[ld[d]] - len(Dz[ld[d]]) < 0
                TARz = sum(ODM[ld[d]])
                DT = (len(Dz[ld[d]]) - nz[ld[d]]) / float(TARz)
                PD = set([])
                append_record(fpath, iterNum, d.did, ld[d], DT, PD)
            else:
                if nz[gd[d]] - len(Dz[gd[d]]) - len(Fz[gd[d]]) >= 0:
                    DT = 0
                else:
                    TARz = sum(ODM[gd[d]])
                    DT = (len(Dz[gd[d]]) + len(Fz[gd[d]]) - nz[gd[d]]) / float(TARz)
                PD = Dz[gd[d]]
                append_record(fpath, iterNum, d.did, gd[d], DT, PD)
        #
        Dz = {zid: set() for zid in Z}
        for d in D.itervalues():
            if gd[d] != None:
                zid = Bz[gd[d]].get()
            else:
                zid = Bz[ld[d]].get()
            Dz[zid].add(d)
            ld[d] = zid
        iterNum += 1

        #
        # if DISPLAY_LOG:
        #     print
        #     print '------------------------------------%d' % iterNum
        #     print 'current driver position'
        #     for z, z_drivers in Dz.iteritems():
        #         print 'z %d: %s' % (z, str(z_drivers))
        #     print
        #     print 'unit arrivals'
        #     for z in Z:
        #         print 'z %d: %s' % (z, str(nz[z]))
        #     print
        #     print 'L: %s' % str([str(d) for d in L])
        #     print 'FD: %s' % str([str(d) for d in FD])
        #     print 'UD: %s' % str([str(d) for d in UD])
        #     print 'F: %s' % str([str(d) for d in F])
        #     print



class driver(object):
    def __init__(self, did):
        self.did = did
        self.dsGAP_memory = {}

    def set_community(self, cid, Cd):
        self.cid, self.Cd = cid, Cd

    def __repr__(self):
        return 'did%d(c%d)' % (self.did, self.cid)

    def update_memory(self, zid, dsGAP):
        if not self.dsGAP_memory.has_key(zid):
            self.dsGAP_memory[zid] = 0
        self.dsGAP_memory[zid] = (self.dsGAP_memory[zid] + dsGAP) / 2.0


if __name__ == '__main__':
    # comStructure = [
    #     [1],
    #     [2], [3],
    #     [4, 5, 6],
    #     [7, 8, 9],
    #     [10, 11, 12]
    # ]

    comStructure = [
        [1],
        [2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12]
    ]

    M = [
        [0, 0, 0, 1, 1],
        [0, 0, 0, 2, 1],
        [0, 0, 0, 1, 2],
        [0, 0, 1, 0, 0],
        [1, 1, 0, 0, 0]
    ]


    gen_synTrajectories(2, comStructure, M)