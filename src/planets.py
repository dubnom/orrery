#!/usr/bin/python3
import math
from datetime import datetime, timedelta
import numpy as np
from astropy.time import Time
from astroquery.jplhorizons import Horizons

names = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

def planetAngle(name, time):
    nasaid = 1 + names.index(name)
    obj = Horizons(id=nasaid, location="@sun", epochs=time, id_type=None).vectors()
    return math.degrees(math.atan2(obj['y'][0], obj['x'][0])) % 360


import orrery

td = timedelta(days=30)
dt = datetime(2018,2,6)

mins = [0] * 8
maxs = [0] * 8

for w in range(12*5):
    time = Time(dt).jd
    angs = []
    for name in names:
        angle = planetAngle(name, time)
        cAngle = orrery.planetLocation(name, dt)[0]
        error = int(cAngle - angle)
        if error > 180:
            error = 360 - error
        elif error < -180:
            error += 360
        angs.append(error)
    print(dt, ','.join(map(str,angs)))
    mins = [min(x, y) for x, y in zip(mins, angs)]
    maxs = [max(x, y) for x, y in zip(maxs, angs)]
    dt += td

print(','.join(map(str,mins)))
print(','.join(map(str,maxs)))
