import __init__
from init_project import *
#

fpath = opath.join(dpath['zonePoints'], 'zonePoints-zi(52)zj(9).pkl')

zonePoints = None
with open(fpath, 'rb') as fp:
    zonePoints = pickle.load(fp)
text = ''
for d in zonePoints:
    print d
    if d.has_key('amenity'):
        text += ' %s' % d['amenity']
    if d.has_key('name'):
        text += ' %s' % d['name']
    if d.has_key('tourism'):
        text += ' %s' % d['tourism']
print text
# dpath['zonePolygons']

#
# import matplotlib.pyplot as plt
# from wordcloud import WordCloud
#
# # text = 'all your base are belong to us all of your base base base'
# wordcloud = WordCloud(background_color="white",
#                       # relative_scaling = 1.0,
#                       # stopwords = 'to of'
#                         max_font_size=40,
#                       ).generate(text)
# plt.imshow(wordcloud)
# plt.axis("off")
# plt.show()

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from os import path
d = path.dirname(__file__)
alice_mask = np.array(Image.open(opath.join(d, "Picture1.png")))

# wordcloud = WordCloud().generate(text)
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(#max_font_size=40,
                      background_color="white", mask=alice_mask).generate(text)

wordcloud.to_file(opath.join(d, "alice.png"))

plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

plt.imshow(alice_mask, cmap=plt.cm.gray, interpolation='bilinear')
plt.axis("off")
plt.show()