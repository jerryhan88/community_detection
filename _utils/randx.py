from random import random, randint

"""
    A fast discrete random variable with arbitrary frequency
    distribution generator. 

    Based on "An Efficient Method for Generating Discrete 
    Random Variables With General Distributions", A.J. 
    Walker, University of Witwatersrand, South Africa. ACM
    Transactions on Mathematical Software, Vol. 3, No. 3, 
    September 1977, Pages 253-256. 

    Constructor takes a single parameter, e, that contains 
    the desired probability values. 

    >> a = ArbRand([0.5, 0.4, 0.1])
    >> a.get()
    2
    >>
    
    NOTE source from http://pastebin.com/zAhMjUZW
"""

class ArbRand:
    """ Generates the list of cutoff values """
    def __init__(self, e, error=1E-6):
        assert abs(sum(e) - 1.0) <= error
        # Populate b, ia, f
        b = [x - (1.0 / float(len(e))) for x in e]
        self.f = [0.0] * len(e)
        self.ia = range(len(e))
        #p = [0.0] * len(e)

        # Find the largest positive and negative differences
        # and their positions in b
        for _ in xrange(len(e)): 
            # Check if the sum of differences in B have become
            # significant 
            if (sum(map(abs, b)) < error): break

            c = min(b)
            d = max(b)
            k = b.index(c)
            l = b.index(d)

            # Assign the cutoff values
            self.ia[k] = l
            self.f[k] = 1.0 + (c * float(len(e)))
            b[k] = 0.0
            b[l] = c + d

    """ Returns a value based on the pmf provided """
    def get(self):
        ix = randint(0, len(self.f) - 1)
        if (random() > self.f[ix]):  ix = self.ia[ix]
        return ix


def test_ArbRand():
    N = 10000
    g = ArbRand([0.5, 0.4, 0.1])
    a = [0] * 3
    for _ in xrange(N):
        a[g.get()] += 1
    print a, [x / float(N) * 100 for x in a]

if __name__ == '__main__':
    test_ArbRand()
