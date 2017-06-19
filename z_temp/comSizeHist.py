import __init__
from init_project import *

fpath = opath.join(dpath['communityStats'], 'communityStats-2009-summary.csv')
df = pd.read_csv(fpath)

df['numDrivers'].quantile(.25)
df['numDrivers'].quantile(.5)
df['numDrivers'].quantile(.75)
df['numDrivers'].quantile(.9)
