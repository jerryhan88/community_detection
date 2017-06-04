import __init__
from init_project import *

import pandas as pd
HOUR1 = 3600


fpath = opath.join(dpath['pickupDistance'], 'pickupDistance-2009-10.csv')
df = pd.read_csv(fpath)
df = df[(df['dwellTime'] != 0) & (df['dwellTime'] < HOUR1)]
df = df.sort_values(['month', 'day', 'hour'], ascending=[True, True, True])


df['dwellTime'].mean()
df['dwellTime'].hist()

_did0 = '37853'
df[(df[_did0] != 0)][['month', 'day', 'hour', 'lon', 'lat', 'zi', 'zj', 'dwellTime', 'distance', _did0]]


fpath = opath.join(dpath['individualCounting'], 'new.csv')
df_new = pd.read_csv('new.csv')
