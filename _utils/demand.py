from random import expovariate
from itertools import chain
from randx import ArbRand


class od_matrix(object):
    def __init__(self, N, M):
        '''
        N: nodes
        M = [m_ij]: OD matrix
          m_ij: arrival rate of customers from N[i] to node N[j]
        A: [(period length, arrival rate), ...]
          Total arrival rate schedule (revolutionary)
        
        TAR: total arrival rate
        R: discrete empirical random variate generator
        OD: origin-destination table corresponding to R
        
        LARS: length of arrival rate schedule
        ICARP: index of current arrival rate period
        ECARP: end of current arrival rate period
        
        NAT: next arrival time

        NOTE
          If A == None, then use TAR as it is, 
          Else ...
        '''
        # prepare TAR, R, OD.
        assert len(N) == len(M) and all(len(Mj) == len(N) for Mj in M)
        assert all(all(mij >= 0 for mij in Mi) for Mi in M)
        X = list(chain(*M))
        self.TAR = sum(X)
        self.P = [x / float(self.TAR) for x in X]
        self.R = ArbRand(self.P)
        self.OD = [(N[i], N[j]) for i in xrange(len(N)) for j in xrange(len(N))]
        # prepare LARS, ICARP, ECARP
        self.A = [(None, self.TAR)]
        self.LARS = None
        self.ICARP = 0
        self.ECARP = 1e400

        # set initial NAT.
        self.NAT = 0
        self.next_arrival()

    def next_arrival(self):
        t = self.NAT
        self.NAT += expovariate(self.A[self.ICARP][1])
        while self.NAT > self.ECARP:
            self.ICARP += 1
            if self.ICARP == len(self.A):
                self.ICARP = 0
            SCARP = self.ECARP  # start of current (with index ICARP) arrival rate period
            self.ECARP += self.A[self.ICARP][0]
            if self.A[self.ICARP][1] == 0:
                self.NAT = self.ECARP + 1  # 1 is arbitrary number.
            else:
                self.NAT = SCARP + expovariate(self.A[self.ICARP][1])
        return t, self.OD[self.R.get()]

    def get_unit_arrivals(self):
        init_time = self.NAT = int(self.NAT)
        unit_arrivals = {}
        while True:
            t, (o, d) = self.next_arrival()
            if t - init_time > 1:
                break
            unit_arrivals.setdefault(o, []).append(d)
        return unit_arrivals


def test():
    N = ['a', 'b', 3]
    M = [[0, 4, 7],
         [1, 0, 1],
         [2, 2, 0]]
    A = [(100, 0.1), (50, 0.2), (50, 0.3)]
    ODM = od_matrix(N, M)
    # ODM = od_matrix(N, M, A)
    print '\n'.join('%s --> %s: %5.1f%%' % (o, d, p * 100) for ((o, d), p) in zip(ODM.OD, ODM.P))
    for i in xrange(1, 101):
        t, (o, d) = ODM.next_arrival()
        print '%d (%.3f): %s --> %s' % (i, t, o, d)

if __name__ == '__main__':
    test()
