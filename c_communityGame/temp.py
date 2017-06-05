import __init__
from init_project import *
#
from random import normalvariate, randint, sample, seed
from itertools import chain

LAMBDA = 0.9

class agent(object):
    def __init__(self, aid, com_id, com_members, agents, num_zones):
        self.aid = aid
        self.com_id, self.com_members = com_id, com_members
        self.agents = agents
        self.info = []
        self.reward_memory = [0] * num_zones

    def __repr__(self):
        return 'aid %d' % self.aid

    def init_info(self):
        self.info = []

    def broadcast_info(self, zid, reward):
        for aid in self.com_members:
            if aid == self.aid:
                continue
            self.agents[aid].info += [(zid, reward)]

    def get_max_reward(self):
        max_zid, max_reward = None, -1e400
        for i, reward in enumerate(self.reward_memory):
            if max_reward < reward:
                max_zid, max_reward = i, reward
        return max_zid, max_reward

    def update_reward(self, zid, actual_reward):
        self.reward_memory[zid] = (1 - LAMBDA) *self.reward_memory[zid] + LAMBDA * actual_reward



seed(0)


# Reward distribution (using normal distribution)
#  [(mean0, std0), (mean1, std1), ...]
num_zones = 9
reward_dists = [(0, 3),  (5, 1), (0, 5),
                (-1, 2), (3, 4), (4, 2),
                (-2, 3), (3, 1), (4, 1)]
assert len(reward_dists) == num_zones

communities = [[1],
               [2, 3],
               [4, 5, 6]
               ]
agents = {}
for i, members in enumerate(communities):
    for aid in members:
        agents[aid] = agent(aid, i, members, agents, num_zones)


while True:
    # choose leaders
    leaders = set()
    for members in communities:
        num_leader = randint(0, len(members))
        leaders = leaders.union(set(sample(members, num_leader)))
    #
    for a in agents.itervalues():
        a.init_info()
    # generate reward
    rewards = [normalvariate(m, s) for m, s in reward_dists]
    zid_leaders = {zid: [] for zid in xrange(num_zones)}
    for lid in leaders:
        chosen_zid = randint(0, len(rewards))
        reward = rewards[chosen_zid]
        agents[lid].broadcast_info(chosen_zid, reward)
        zid_leaders[chosen_zid] += [lid]
    #
    followers = set(agents.keys()).difference(leaders)
    fid_decision = {}
    zid_numFollowers = {zid: 0 for zid in xrange(num_zones)}
    for fid in followers:
        max_zid, max_reward = agents[fid].get_max_reward()
        for zid, reward in agents[fid].info:
            if max_reward < reward:
                max_zid, max_reward = zid, reward
        fid_decision[fid] = max_zid
        zid_numFollowers[max_zid] += 1
    #
    for fid, decision_zid in fid_decision.iteritems():
        actual_reward = 0
        if rewards[decision_zid] >= 0:
            actual_reward += rewards[decision_zid] / float(zid_numFollowers[decision_zid])
        else:
            actual_reward -= rewards[decision_zid] * float(zid_numFollowers[decision_zid])
        agents[fid].update_reward(decision_zid, actual_reward)
        print fid, actual_reward, zid_leaders[decision_zid]


    assert False

