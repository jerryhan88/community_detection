import __init__
from init_project import *

from d1_inputs import f_map_comStructure, f_map_netDemand, prefStrength, numSimRun


import matplotlib.pyplot as plt

mlists = (
    'x',  #    x
    'o',  #    circle
    'p',  #    pentagon
    '*',  #    star
    'D',  #    diamond
    'v',  #    triangle_down


    '^',  #    triangle_up
    '<',  #    triangle_left
    '>',  #    triangle_right
    's',  #    square
    '+',  #    plus

    'h',  #    hexagon1
    '1',  #    tri_down
    '2',  #    tri_up
    '3',  #    tri_left
    '4',  #    tri_right
    '8',  #    octagon
    'H',  #    hexagon2
    'd',  #    thin_diamond
    '|',  #    vline
    '_',  #    hline
    '.',  #    point
    ',',  #    pixel

    'D',  #    diamond
    '8',  #    octagon
          )
          
results = {}
for ps in prefStrength:
    for cs in f_map_comStructure.iterkeys():
        for (ns, da) in f_map_netDemand:
            ifpath = opath.join(dpath['relationSummary'],
                                        'relationSummary-ps(%.2f)-cs(%s)-ns(%s)-da(%s).csv' % (ps, cs, ns, da))
            df = pd.read_csv(ifpath)
            results[ps, cs, ns, da] = {'numMissingRel': df['numMissingRel'].mean(),
                                        'numWrongRel': df['numWrongRel'].mean(),
                                        'numPosRel': df['numPosRel'].mean()
            }
        

def scatter_charts():
    for cs in f_map_comStructure.iterkeys():
        for ps in prefStrength:
            fn = 'scatterChart-ps(%.2f)-cs(%s).pdf' % (ps, cs)
            ofpath = opath.join(dpath['relationChart'], fn)
            #
            _figsize = (8, 6)
            _fontsize = 14
            _xlabel = '# of $MR$'
            _ylabel = '# of $WR$'
            #
            fig = plt.figure(figsize=_figsize)
            ax = fig.add_subplot(111)

            plots, labels = [], []
            i = 0
            for ns in ['S', 'M']:
                for da in 'L M H'.split():
                    p = plt.scatter(results[ps, cs, ns, da]['numMissingRel'], results[ps, cs, ns, da]['numWrongRel'],
                                    marker=mlists[i])
                    plots += [p]
                    labels += ['$Z(%s)$-$D(%s)$' % (ns, da)]
                    i += 1
            plt.legend(plots, labels, loc='upper right', ncol=2, fontsize=_fontsize, scatterpoints=1)
            ax.set_xlabel(_xlabel, fontsize=_fontsize + 2)
            ax.set_ylabel(_ylabel, fontsize=_fontsize + 2)
            ax.tick_params(axis='both', which='major', labelsize=_fontsize)
            plt.savefig(ofpath, bbox_inches='tight', pad_inches=0)

def line_charts():
    for cs in f_map_comStructure.iterkeys():
        for (ns, da) in f_map_netDemand:
            for m in ['numMissingRel', 'numWrongRel', 'numPosRel']:
                fn = 'lineChart-%s-cs(%s)-ns(%s)-da(%s).pdf' % (m, cs, ns, da)
                ofpath = opath.join(dpath['relationChart'], fn)
                X, Y = [], []
                for ps in prefStrength:
                    X += [ps]
                    Y += [results[ps, cs, ns, da][m]]

                _figsize = (8, 6)
                if m == 'numMissingRel':
                    _ylabel = 'The number of missing relations'
                elif m == 'numWrongRel':
                    _ylabel = 'The number of wrong relations'
                elif m == 'numPosRel':
                    _ylabel = 'The number of positive relations'
                else:
                    assert False
                _xlabel = '$ps$'
                _fontsize = 14
                #
                fig = plt.figure(figsize=_figsize)
                ax = fig.add_subplot(111)
                ax.set_xlabel(_xlabel, fontsize=_fontsize)
                ax.set_ylabel(_ylabel, fontsize=_fontsize)
                plt.plot(X, Y, linewidth=1)
                #
                plt.savefig(ofpath, bbox_inches='tight', pad_inches=0)




def multiLines_charts():
    for cs in f_map_comStructure.iterkeys():
        for (ns, da) in f_map_netDemand:
            fn = 'multiLinesChart-cs(%s)-ns(%s)-da(%s).pdf' % (cs, ns, da)
            ofpath = opath.join(dpath['relationChart'], fn)
            _figsize = (8, 6)
            _xlabel = '$ps$'
            _fontsize = 14
            #
            fig = plt.figure(figsize=_figsize)
            ax = fig.add_subplot(111)
            labels = []
            ymax = -1e400

            m = 'numMissingRel'
            X, Y = [], []
            for ps in prefStrength:
                X += [ps]
                Y += [results[ps, cs, ns, da][m]]
                if ymax < results[ps, cs, ns, da][m]:
                    ymax = results[ps, cs, ns, da][m]
            _label = '# of $MR$'
            labels += [_label]
            plt.plot(X, Y, linewidth=1, marker=mlists[0])



            m = 'numWrongRel'
            X, Y = [], []

            for ps in prefStrength:
                X += [ps]
                Y += [results[ps, cs, ns, da][m]]
                if ymax < results[ps, cs, ns, da][m]:
                    ymax = results[ps, cs, ns, da][m]

            _label = '# of $WR$'
            labels += [_label]
            plt.plot(X, Y, linewidth=1, marker=mlists[1])
            plt.legend(labels, loc='upper left', ncol=1, fontsize=_fontsize)
            ax.set_xlabel(_xlabel, fontsize=_fontsize + 2)
            ax.set_ybound(upper=ymax * 1.1)
            ax.tick_params(axis='both', which='major', labelsize=_fontsize)
            #
            plt.savefig(ofpath, bbox_inches='tight', pad_inches=0)



if __name__ == '__main__':
    scatter_charts()
    # line_charts()
    # multiLines_charts()