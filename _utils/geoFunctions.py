from init_project import *
#
import os.path as opath
import numpy as np
from geopy.distance import VincentyDistance
import csv

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
    sgMainBorder = np.array(sgMainBorder)
    np.save(ofpath, sgMainBorder)
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
    lons = np.array([])
    x = min_lon
    while x < max_lon:
        lons = np.append(lons, x)
        p0 = [min_lat, x]
        moved_point = mover.destination(point=p0, bearing=EAST)
        x = moved_point.longitude
    np.save(lons_ofpath, lons)
    #
    lats = np.array([])
    y = min_lat
    while y < max_lat:
        lats.append(y)
        p0 = [y, min_lon]
        moved_point = mover.destination(point=p0, bearing=NORTH)
        y = moved_point.latitude
    lons.sort(); lats.sort()
    save_pickle_file(ofpath, [lons, lats])
    return lons, lats