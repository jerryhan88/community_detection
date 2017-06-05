import __init__
from init_project import *

import statsmodels.api as sm
import pandas as pd
HOUR1 = 3600


fpath = opath.join(dpath['pickupDistance'], 'pickupDistance-2009-4237.csv')
df = pd.read_csv(fpath)
df = df[(df['dwellTime'] != 0) & (df['dwellTime'] < HOUR1)]
df = df.sort_values(['month', 'day', 'hour'], ascending=[True, True, True])
_did0 = '26937'
df[(df[_did0] != 0)][['month', 'day', 'hour', 'lon', 'lat', 'zi', 'zj', 'dwellTime', _did0]]


numObservations = len(df)
num_encouters = 0
zones = set()
for encounter, zi, zj in df[[_did0, 'zi', 'zj']].values:
    if encounter != 0:
        num_encouters += 1
        zones.add('%d#%d' % (zi, zj))

did0_df = df[[_did0, 'zi', 'zj', 'dwellTime']]
did0_df['zizj'] = did0_df.apply(lambda row: '%d#%d' % (row['zi'], row['zj']), axis=1)
for zizj in zones:
    did0_df['z'+zizj] = np.where(did0_df['zizj'] == zizj, 1, 0)
if num_encouters < len(zones) + 1 + 1:
    assert False

y = did0_df['dwellTime']
X = did0_df[[_did0] + ['z'+zizj for zizj in zones]]
X = sm.add_constant(X)
res = sm.OLS(y, X, missing='drop').fit()
print res.summary()


df.groupby(['zi', 'zj']).count()['dwellTime']
df.groupby(['zi', 'zj']).mean()['dwellTime']


df[(df['zi'] == 50) & (df['zj'] == 9)]['dwellTime']

df['dwellTime'].mean()
df['dwellTime'].hist()


fpath = opath.join(dpath['individualCounting'], 'new.csv')
df_new = pd.read_csv(fpath)
df_new.sort_values(['numEncounters'], ascending=[False]).loc[:5]

