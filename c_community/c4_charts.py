import __init__
from init_project import *
#

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import seaborn as sns; sns.set(style="ticks", color_codes=True)


ifpath = opath.join(dpath['communityStats'], 'communityStats-2009-summary.csv')


def scatterPlotWithRegLine():
    df = pd.read_csv(ifpath)
    df = df[(df['numDrivers'] < 200) & (df['numDrivers'] > 10)]
    df['vacantRate'] = df['vacantRate'].round(2)
    xyPair_labels = {('numDrivers', 'graphDensity'): ('Drv #', 'DenC'),
                     ('dwellTimePT', 'vacantRate'): ('DTime', 'Va'),
                     ('avgEdgeW', 'vacantRate'): ('EdgeW', 'Va'),
                     ('avgEdgeW', 'dwellTimePT'): ('EdgeW', 'DTime'),
                     }
    for (x_n, y_n), (x_l, y_l) in xyPair_labels.iteritems():
        fn = 'scatter_%s_%s.pdf' % (x_n, y_n)
        ofpath = opath.join(dpath['communityStats'], fn)
        _figsize = (8, 6)
        _fontsize = 28
        fig = plt.figure(figsize=_figsize)
        ax = fig.add_subplot(111)
        x, y = pd.Series(df[x_n], name=x_l), pd.Series(df[y_n], name=y_l)
        sns.regplot(x=x, y=y, marker='X', color="black")

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.set_xlabel(x_l, fontsize=_fontsize)
        ax.set_ylabel(y_l, fontsize=_fontsize)
        ax.tick_params(axis='both', which='major', labelsize=_fontsize)
        plt.savefig(ofpath, bbox_inches='tight', pad_inches=0)

def pairCorrelationPlot():
    df = pd.read_csv(ifpath)
    # sns.set(font_scale = 1.5, rc={'axes.facecolor':'white', 'figure.facecolor':'white'})
    df_cn = df[[cn for cn in df.columns if cn != 'comName']]
    sns.pairplot(df_cn)
    #
    subset_df = df_cn[['numDrivers', 'graphDensity',
                       'numTripsPD', 'operationHourPD', 'durationPD', 'vacantRate',
                       'farePD', 'dwellTimePT', 'avgEdgeW']]
    subset_df = subset_df[(subset_df['numDrivers'] > 5)]
    sns.pairplot(subset_df)
    #
    subset_df = subset_df[(subset_df['numDrivers'] < 200) & (subset_df['numDrivers'] > 10)]
    sns.pairplot(subset_df, kind="reg")

if __name__ == '__main__':
    scatterPlotWithRegLine()