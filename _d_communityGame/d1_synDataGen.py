import __init__
from init_project import *
#
from _utils.logger import get_logger
#
from random import uniform, randint, sample, seed, expovariate
import csv

LAMBDA = 0.01

logger = get_logger()


def run(seedNum):
    seed(seedNum)
    fpath = opath.join(dpath['synData'], 'synData-%d.csv' % seedNum)
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = ['iterNum', 'did', 'zid', 'reward', 'prevAgents', 'cost_memory']
        writer.writerow(header)

    # demand_distributions = [
    #                 (2, 2), (2, 2), (2, 2),
    #                 (2, 2), (1, 3), (2, 2),
    #                 (2, 2), (2, 2), (2, 2),
    #                 ]

    demand_distributions = [
        (2, 4), (2, 4), (2, 5),
        (2, 5), (1, 3), (2, 4),
        (2, 5), (2, 4), (2, 5),
    ]

    # demand_distributions = [
    #     0.5, 0.5, 0.5, 0.5,
    #     0.5, 0.1, 0.5,
    #     0.5, 0.5, 0.5,
    # ]


    num_zones = len(demand_distributions)

    communities = [[1],
                   [2, 3],
                   [4, 5, 6],
                   # [7, 8],
                   # [9, 10, 11],
                   ]
    agents = {}
    for i, members in enumerate(communities):
        for aid in members:
            agents[aid] = agent(aid, i, members, agents, num_zones)

    logger.info('start synData generation %s')
    numIter = 0
    while True:
        numIter += 1
        if numIter % 100 ==0:
            logger.info('numIter %d' % numIter)

        # choose leaders
        leaders = set()
        for members in communities:
            num_leader = randint(0, len(members))
            leaders = leaders.union(set(sample(members, num_leader)))
        #
        for a in agents.itervalues():
            a.init_info()
        # generate demands
        generated_demands = [uniform(a, b) for a, b in demand_distributions]
        # generated_demands = [expovariate(l) for l in demand_distributions]
        zid_leaders = {zid: [] for zid in xrange(num_zones)}
        for lid in leaders:
            chosen_zid = randint(0, len(generated_demands) - 1)
            demand = generated_demands[chosen_zid]
            agents[lid].broadcast_info(chosen_zid, demand)
            zid_leaders[chosen_zid] += [lid]
        #
        followers = set(agents.keys()).difference(leaders)
        fid_decision = {}
        zid_numFollowers = {zid: 0 for zid in xrange(num_zones)}
        for fid in followers:
            min_zid, min_cost = agents[fid].get_min_cost()
            for zid, demand in agents[fid].info:
                cost = 1 / float(demand)
                if cost < min_cost :
                    min_zid, min_cost = zid, cost
            fid_decision[fid] = min_zid
            zid_numFollowers[min_zid] += 1
        #


        if numIter < 2000:
            continue
        elif numIter < 10000:
            for fid, decision_zid in fid_decision.iteritems():
                # actual_cost = zid_numFollowers[decision_zid] / float(generated_demands[decision_zid])
                actual_cost = 1 / float(generated_demands[decision_zid])
                with open(fpath, 'a') as w_csvfile:
                    writer = csv.writer(w_csvfile, lineterminator='\n')
                    writer.writerow([numIter, fid, decision_zid, actual_cost, '|'.join(map(str, zid_leaders[decision_zid])),
                                     agents[fid].cost_memory])
        else:
            break
        for fid, decision_zid in fid_decision.iteritems():
            # actual_cost = zid_numFollowers[decision_zid] / float(generated_demands[decision_zid])
            actual_cost = 1 / float(generated_demands[decision_zid])
            # if rewards[decision_zid] >= 0:
            #     # actual_reward += rewards[decision_zid] / float(zid_numFollowers[decision_zid])
            #     actual_cost += rewards[decision_zid]
            # else:
            #     actual_cost -= rewards[decision_zid] * float(zid_numFollowers[decision_zid])
            agents[fid].update_cost(decision_zid, actual_cost)


class agent(object):
    def __init__(self, aid, com_id, com_members, agents, num_zones):
        self.aid = aid
        self.com_id, self.com_members = com_id, com_members
        self.agents = agents
        self.info = []
        self.cost_memory = [0] * num_zones

    def __repr__(self):
        return 'did %d' % self.aid

    def init_info(self):
        self.info = []

    def broadcast_info(self, zid, reward):
        for aid in self.com_members:
            if aid == self.aid:
                continue
            self.agents[aid].info += [(zid, reward)]

    def get_min_cost(self):
        min_zid, min_cost = None, 1e400
        for i, cost in enumerate(self.cost_memory):
            if cost < min_cost:
                min_zid, min_cost = i, cost
        return min_zid, min_cost

    def update_cost(self, zid, actual_cost):
        self.cost_memory[zid] = (1 - LAMBDA) * self.cost_memory[zid] + LAMBDA * actual_cost


if __name__ == '__main__':
    run(3)
    # run(7)

