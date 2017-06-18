import __init__
from init_project import *
#
from _utils.geoFunctions import viz_interactionHotspots

meaningless_keys = set('geometry osm_id tags ref'.split())
for keys in ['bridge railway highway motorcar bicycle aeroway aerialway foot tower:type tunnel horse',
            'natural water covered access place landuse way_area area waterway surface wetland',
            'operator brand barrier power boundary military',
            'building man_made disused service junction oneway',
            'population width z_order ele layer']:
    meaningless_keys = meaningless_keys.union(set(keys.split()))


def run(processorID, numWorkers=11):
    for i, fn in enumerate([fn for fn in os.listdir(dpath['hotspotDetection'])
                            if fnmatch(fn, 'hotspotDetection-*.pkl')]):
        _, _, gn = fn[:-len('.pkl')].split('-')
        if i % numWorkers != processorID:
            continue
        process_group(gn)


def process_group(gn):
    ifpath = opath.join(dpath['hotspotDetection'], 'hotspotDetection-2009-%s.pkl' % gn)
    html_fpath = opath.join(dpath['hotspotDetection'], 'locations-2009-%s.html' % gn)
    wordCloud_fpath = opath.join(dpath['hotspotDetection'], 'wordCloud-2009-%s.png' % gn)
    zoneCoef = None
    with open(ifpath, 'rb') as fp:
        zoneCoef = pickle.load(fp)
    hotspots, zizj_text = [], ''
    word_counts = {}
    for zizj, w in zoneCoef['neg']:
        zi, zj = map(int, zizj.split('#'))
        hotspots += [(zi, zj, w)]
        update_text_zizj(zi, zj, word_counts)
    if not word_counts:
        return None
    for w, c in word_counts.iteritems():
        if c == 0:
            continue
        zizj_text += (' %s' % w) * c
    viz_interactionHotspots(hotspots, html_fpath)
    # wordcloud = WordCloud(max_font_size=40, background_color="white").generate(zizj_text)
    wordcloud = WordCloud(  # max_font_size=40,
        background_color="white", mask=np.array(Image.open("w2h1.png")), collocations=False).generate(zizj_text)
    wordcloud.to_file(wordCloud_fpath)
    # plt.figure()
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")
    # plt.show()


def update_text_zizj(zi, zj, text_counts):
    def process_dictObject(dictObject, text_counts, meaningful_keys):
        for oDict in dictObject:
            for k in oDict.iterkeys():
                if k in meaningless_keys:
                    continue
                w = oDict[k].replace(' ', '_')
                if not text_counts.has_key(w):
                    text_counts[w] = 0
                text_counts[w] += 1
                # for w in oDict[k].split():
                #     if '(' in w or ')' in w:
                #         continue
                #     if '&' in w or '.' in w:
                #         continue
                #     if 'The' in w:
                #         continue
                #     if not text_counts.has_key(w):
                #         text_counts[w] = 0
                #     text_counts[w] += 1
                meaningful_keys.add(k)
        return meaningful_keys
    #
    text, meaningful_keys = '', set()
    #
    points_fpath = opath.join(dpath['zonePoints'], 'zonePoints-zi(%d)zj(%d).pkl' % (zi, zj))
    zonePoints = None
    with open(points_fpath, 'rb') as fp:
        zonePoints = pickle.load(fp)
    meaningful_keys = process_dictObject(zonePoints, text_counts, meaningful_keys)
    #
    polys_fpath = opath.join(dpath['zonePolygons'], 'zonePolygons-zi(%d)zj(%d).pkl' % (zi, zj))
    zonePolys = None
    with open(polys_fpath, 'rb') as fp:
        zonePolys = pickle.load(fp)
    meaningful_keys = process_dictObject(zonePolys, text_counts, meaningful_keys)


if __name__ == '__main__':
    run(2, 3)
    # get_text_zizj(23, 29)