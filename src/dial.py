from datetime import date

year = 2003
dec22 = date(year-1, 12, 22).toordinal()

specialDays = [
        ("Winter Solstice",   12, 21, 22),
        ("Summer Solstice",    6, 20, 21),
        ("Spring Equinox",     3, 21),
        ("Autumnal Equinox",   9, 21),
        ("Richard's Bday",     7,  4),
        ("Glenn's Bday",       4, 20),
        ("Mike's Bday",        8, 23),
]


# Fusion 360 doesn't easily allow angles over 180 degrees

def dateAngle(d):
    zod = d - dec22
    deg = 360 * zod/365
    if deg < 0:
        deg = -deg
        sign = -1
    elif deg > 180:
        deg = 360 - deg
        sign = -1
    else:
        sign = 1
    return (deg, sign)


# Month angles

print("Month Angles")
for month in range(1, 13):
    d = date(year, month, 1).toordinal()
    deg, sign = dateAngle(d)
    print("%2d %7.3f %2d" % (month, deg, sign))
print()


# Special days

print("Special Days")
for v in specialDays:
    name = v[0]
    month = v[1]
    day1 = day2 = v[2]
    if len(v) > 3:
        day2 = v[3]

    d = date(year, month, day1).toordinal()
    deg1, sign = dateAngle(d)
    d = date(year, month, day2).toordinal()
    deg2, sign = dateAngle(d)
    deg = (deg1 + deg2) / 2.
    deg += sign * (360/365/2)
    print("%20s %7.3f %2d" % (name, deg, sign))

