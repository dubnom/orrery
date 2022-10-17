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

for w in range(12*5):
    time = Time(dt).jd
    angs = [str(dt)]
    for name in names:
        angle = planetAngle(name, time)
        cAngle = orrery.planetLocation(name, dt)[0]
        angs.append(str(int(cAngle - angle)))
    print(','.join(angs))
    dt += td
