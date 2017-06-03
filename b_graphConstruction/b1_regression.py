import __init__
from init_project import *
#
import pandas as pd

fpath = opath.join(dpath['pickupDistance'], 'pickupDistance-2009-4.csv')
df = pd.read_csv(fpath)


df['dwellTime'].min()
df['dwellTime'].max()

df[(df['dwellTime'] != 0) & (df['dwellTime'] < 1800)]['dwellTime'].hist()
len(df)
len(df[(df['dwellTime'] != 0) & (df['dwellTime'] < 3600)])
