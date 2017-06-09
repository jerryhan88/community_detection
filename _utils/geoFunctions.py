import __init__
from init_project import *
#
from logger import get_logger
import os.path as opath
from traceback import format_exc
from geopy.distance import VincentyDistance
from shapely.geometry import Polygon
import geopandas as gpd
import numpy as np
import pickle
import csv


logger = get_logger()

NORTH, EAST, SOUTH, WEST = 0, 90, 180, 270


def get_sgMainBorder():
    ofpath = opath.join(dpath['geo'], 'sgMainBorder')
    if opath.exists(ofpath + '.npy'):
        sgBorder = np.load(ofpath + '.npy', 'r+')
        return sgBorder
    ifpath = opath.join(dpath['geo'], 'sgMainBorder_manually.csv')
    sgMainBorder = []
    with open(ifpath, 'rb') as r_csvfile:
        reader = csv.reader(r_csvfile)
        header = reader.next()
        hid = {h: i for i, h in enumerate(header)}
        for row in reader:
            lon, lat = map(eval, [row[hid[cn]] for cn in ['longitude', 'latitude']])
            sgMainBorder += [(lon, lat)]
    np.save(ofpath, np.array(sgMainBorder))
    return sgMainBorder


def get_sgGrid():
    lons_ofpath = opath.join(dpath['geo'], 'sgLons(%.1fkm)' % ZONE_UNIT_KM)
    lats_ofpath = opath.join(dpath['geo'], 'sgLats(%.1fkm)' % ZONE_UNIT_KM)
    if opath.exists(lons_ofpath + '.npy'):
        sgLons = np.load(lons_ofpath + '.npy', 'r+')
        sgLats = np.load(lats_ofpath + '.npy', 'r+')
        return sgLons, sgLats
    #
    min_lon, max_lon = 1e400, -1e400,
    min_lat, max_lat = 1e400, -1e400
    sgMainBorder = get_sgMainBorder()
    for lon, lat in sgMainBorder:
        min_lon, max_lon = min(min_lon, lon), max(max_lon, lon)
        min_lat, max_lat = min(min_lat, lat), max(max_lat, lat)
    #
    mover = VincentyDistance(kilometers=ZONE_UNIT_KM)
    #
    lons = []
    lon = min_lon
    while lon < max_lon:
        lons += [lon]
        p0 = [min_lat, lon]
        moved_point = mover.destination(point=p0, bearing=EAST)
        lon = moved_point.longitude
    lons.sort()
    np.save(lons_ofpath, np.array(lons))
    #
    lats = []
    lat = min_lat
    while lat < max_lat:
        lats += [lat]
        p0 = [lat, min_lon]
        moved_point = mover.destination(point=p0, bearing=NORTH)
        lat = moved_point.latitude
    lats.sort()
    np.save(lats_ofpath, np.array(lats))
    return lons, lats


def get_sgPoints():
    ofpath = opath.join(dpath['geo'], 'sgPoints.pkl')
    sgPoints = None
    if opath.exists(ofpath):
        with open(ofpath, 'rb') as fp:
            sgPoints = pickle.load(fp)
        return sgPoints
    ifpath = opath.join(dpath['geo'], 'singapore_osm_point.geojson')
    df = gpd.read_file(ifpath)
    sgPoints = []
    sgMainBorder = Polygon(get_sgMainBorder())
    for i in xrange(len(df)):
        if not df.loc[i, 'geometry'].within(sgMainBorder):
            continue
        point_info = {}
        for cn in df.columns:
            if not df.loc[i, cn]:
                continue
            point_info[cn] = df.loc[i, cn]
        sgPoints += [point_info]
    with open(ofpath, 'wb') as fp:
        pickle.dump(sgPoints, fp)
    return sgPoints


def get_sgPolygons():
    ofpath = opath.join(dpath['geo'], 'sgPolygons.pkl')
    sgPolygons = None
    if opath.exists(ofpath):
        with open(ofpath, 'rb') as fp:
            sgPolygons = pickle.load(fp)
        return sgPolygons
    ifpath = opath.join(dpath['geo'], 'singapore_osm_polygon.geojson')
    df = gpd.read_file(ifpath)
    sgPolygons = []
    sgMainBorder = Polygon(get_sgMainBorder())
    for i in xrange(len(df)):
        if not df.loc[i, 'geometry'].within(sgMainBorder):
            continue
        poly_info = {}
        for cn in df.columns:
            if not df.loc[i, cn]:
                continue
            poly_info[cn] = df.loc[i, cn]
        sgPolygons += [poly_info]
    with open(ofpath, 'wb') as fp:
        pickle.dump(sgPolygons, fp)
    return sgPolygons


def find_aZone_points(zi, zj, zPoly):
    try:
        ofpath = opath.join(dpath['zonePoints'], 'zonePoints-zi(%d)zj(%d).pkl' % (zi, zj))
        if opath.exists(ofpath):
            return None
        aZone_points = []
        for point_info in get_sgPoints():
            if point_info['geometry'].within(zPoly):
                aZone_points += [point_info]
        with open(ofpath, 'wb') as fp:
            pickle.dump(aZone_points, fp)
    except Exception as _:
        import sys
        with open('%s_%d_%d.txt' % (sys.argv[0], zi, zj), 'w') as f:
            f.write(format_exc())
        raise
    
    
def find_aZone_polygons(zi, zj, zPoly):
    try:
        ofpath = opath.join(dpath['zonePolygons'], 'zonePolygons-zi(%d)zj(%d).pkl' % (zi, zj))
        if opath.exists(ofpath):
            return None
        aZone_polygons = []
        for poly_info in get_sgPolygons():
            if poly_info['geometry'].intersects(zPoly) or poly_info['geometry'].within(zPoly):
                aZone_polygons += [poly_info]
        with open(ofpath, 'wb') as fp:
            pickle.dump(aZone_polygons, fp)
    except Exception as _:
        import sys
        with open('%s_%d_%d.txt' % (sys.argv[0], zi, zj), 'w') as f:
            f.write(format_exc())
        raise


def classify_aZone_objects(processorID, NUM_WORKERS=11):
    lons, lats = get_sgGrid()
    i = 0
    for zi in xrange(len(lons) - 1):
        for zj in xrange(len(lats) - 1):
            i += 1
            if i % NUM_WORKERS != processorID:
                continue
            rightTop = (lons[zi + 1], lats[zj + 1])
            rightBottom = (lons[zi + 1], lats[zj])
            leftBottom = (lons[zi], lats[zj])
            leftTop = (lons[zi], lats[zj + 1])
            zPoly = Polygon([rightTop, rightBottom, leftBottom, leftTop])
            find_aZone_points(zi, zj, zPoly)
            find_aZone_polygons(zi, zj, zPoly)



if __name__ == '__main__':
    ofpath = opath.join(dpath['zonePolygons'], 'zonePolygons-zi(0)zj(6).pkl')

    with open(ofpath, 'rb') as fp:
        sgPolygons = pickle.load(fp)

    print sgPolygons




    # classify_aZone_objects(0)


