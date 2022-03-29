from datetime import datetime


planets = [
    # Planet        Earth Days    X    Y   Driver   Is planet
    ("Mercury",     87.97,       33, 137,   'X',    True ),
    ("Venus",       224.7,       48,  78,   'Y',    True ),
    ("Earth",       365.24,      59,  59,   'Y',    True ),
    ("Mars",        686.98,      79,  42,   'Y',    True ),
    ("Bridge 1",    0,           55, 138,   'X',    False ),
    ("Bridge 2",    0,          138,  55,   'Y',    False ),
    ("Jupiter",     4332.59,     58, 144,   'X',    True ),
    ("Saturn",      10755.70,    59,  59,   'Y',    True ),
    ("Uranus",      30687.17,    97,  34,   'Y',    True ),
    ("Neptune",     60190.03,   151,  27,   'Y',    True ),
]

# Define Two Line Elements for Starman
s = '1 43205U 18017A   18038.22157858  .00505133 -52681-6  23951-2 0  9997'
t = '2 43205  29.0196 286.7252 3400758 181.1849 342.1043  8.76376464    24'

if False:
    # Test the gear ratios and calculate error
    xAxelSpeed = 88 
    yAxelSpeed = 0
    print('%12s %8s %8s %7s' % ('Planet','Days','Orrery','Error'))
    for (name,days,x,y,driver,ip) in planets:
        if 'X' == driver:
            # X Axis is driving
            if ip:
                print('%12s %8g %8g %7.2f%%' % (name, days, xAxelSpeed, 100*(days - xAxelSpeed)/days))
            yAxelSpeed = xAxelSpeed * y / x;
        else:
            # Y Axis is driving
            xAxelSpeed = yAxelSpeed * x / y;
            if ip:
                print('%12s %8g %8g %7.2f%%' % (name, days, xAxelSpeed, 100*(days - xAxelSpeed)/days))
    exit(0)

if False:
    # Test JPL Ephmerides
    from jplephem.spk import SPK
    p = SPK.open('../data/wld11206.15')
    print(p)
    exit(1)

if False:
    # Astropy
    from astropy.time import Time, TimeDelta
    from astropy import coordinates

    coordinates.solar_system_ephemeris.set('../data/wld11206.15')
    print(coordinates.solar_system_ephemeris.bodies)

    T = Time.now()
    print(T.jd)
    print(coordinates.get_body('902617703', T, ephemeris='../data/wld11206.15'))
    exit(0)


if False:
    # Create and rotate our own ellipse
    import numpy as np
    from matplotlib import pyplot as plt
    from math import pi, cos, sin, radians

    u=(1.6637 + .98613) / 2 - .98613    #x-position of the center
    v=0.0                               #y-position of the center
    a=(1.6637 + .98613) / 2             #radius on the x-axis
    b=(1.6637 - .98613) / 2             #radius on the y-axis
    t_rot=2 * pi * (37/365)             #rotation angle

    t = np.linspace(0, 2*pi, 100)
    Earth = np.array([np.cos(t), np.sin(t)])

    Ell = np.array([a*np.cos(t) , b*np.sin(t)])  
        #u,v removed to keep the same center location
    R_rot = np.array([[cos(t_rot) , -sin(t_rot)],[sin(t_rot) , cos(t_rot)]])  
        #2-D rotation matrix

    Ell_rot = np.zeros((2,Ell.shape[1]))
    for i in range(Ell.shape[1]):
         Ell_rot[:,i] = np.dot(R_rot,Ell[:,i])

    fig, ax = plt.subplots()
    ax.plot( Earth[0,:], Earth[1,:] )
    ax.plot( Ell[0,:] , Ell[1,:] )     #initial ellipse
    ax.plot( u+Ell[0,:] , v+Ell[1,:] )     #initial ellipse
    ax.plot( u+Ell_rot[0,:] , v+Ell_rot[1,:],'darkorange' )    #rotated ellipse
    ax.grid(color='lightgray',linestyle='--')
    ax.set_aspect('equal','box')
    fig.savefig('starman.png')
    exit(0)

if True:
    # Create a plot of earch, mars, and starman (through gearing)
    import numpy as np
    from matplotlib import pyplot as plt
    from math import pi, cos, sin, radians, degrees
    from astropy.time import Time, TimeDelta
    from astropy import coordinates
    from pprint import pprint

    earth_radius = 1.
    mars_radius = 1.524
    sm_arm = 1.32 * earth_radius
    sm_epi = .34 * earth_radius
    sm_ang = radians(360*-37/365)

    def starman(T):
        # Translate T into number of days since 2018 Feb 6
        epoch = Time('2018-02-06')
        days = (T - epoch).to_value('jd')
        angle = radians(360*days/557) + radians(360*(37+91.25)/365)
        return sm_arm*cos(angle)+sm_epi*cos(sm_ang), sm_arm*sin(angle)+sm_epi*sin(sm_ang)

    planetInfoOld = {
            'Mercury':  (Time('2018-02-06'),    87.97,      .39,    radians(283), 0, 0),
            'Venus':    (Time('2018-02-06'),    224.7,      .723,   radians(330), 0, 0),
            'Earth':    (Time('2018-02-06'),    365.25636,  1,      pi/2+radians(360*37/365), 0, 0),  
            'Starman':  (Time('2018-02-06'),    557,        1.32,   pi/2+radians(360*37/365), sm_epi*cos(sm_ang), sm_epi*sin(sm_ang)),
            'Mars':     (Time('2018-02-06'),    686.98,     1.524,  radians(215), 0, 0),
            'Jupiter':  (Time('2018-02-06'),    4332.59,    5.203,  0, 0, 0), 
            'Saturn':   (Time('2018-02-06'),    10755.70,   9.539,  0, 0, 0),
            'Uranus':   (Time('2018-02-06'),    30687.17,   19.18,  0, 0, 0),
            'Neptune':  (Time('2018-02-06'),    60190.03,   30.06,  0, 0, 0),
            }

    planetInfo = {
            'Mercury': (87.97, 0.448407, 5.05985, 0, 0, 1),
            'Venus': (224.7, 0.727912, 5.80397, 0, 0, 2),
            'Earth': (365.256, 0.986066, 2.38918, 0, 0, 3),
            #'Starman': (557, 1.32, 2.38918, sm_epi*cos(sm_ang), sm_epi*sin(sm_ang), 3.32),
            'Starman': (557, .75+.98*3, 2.38918, .75*cos(sm_ang), .75*sin(sm_ang), 2.94 + .75),
            'Mars': (686.98, 1.59736, 3.67414, 0, 0, 4),
            'Jupiter': (4332.59, 5.42634, 3.85817, 0, 0, 5),
            'Saturn': (10755.7, 10.0658, 4.7359, 0, 0, 6),
            'Uranus': (30687.2, 19.8964, 0.479293, 0, 0, 7),
            'Neptune': (60190, 29.9449, 5.9957, 0, 0, 8),
            }

    planetNames = ['Mercury', 'Venus', 'Earth', 'Starman', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
    
    
    epoch = Time('2018-02-06')
    def planetLocation(name, T):
        daysPerYear, radius, aOffset, xOffset, yOffset, pn = planetInfo[name]
        days = (T - epoch).to_value('jd')
        angle = radians(360*days/daysPerYear) + aOffset
        return angle % (2*pi), radius, xOffset, yOffset, pn

    TT = Time('2018-02-06')

    if False:
        # Create info table
        print("planetInfo = {")
        for planet in planetNaes:
            try:
                pos = coordinates.get_body(planet, TT).heliocentricmeanecliptic
                daysPerYear = planetInfoOld[planet][1]
                print("    '%s': (%g, %g, %g, %g, %g)," % (planet, daysPerYear, pos.distance.value, radians(pos.lon.value), 0, 0))
            except:
                pass
        print("}")

    for T in (TT, Time.now()):
        print(TT)
        print('Earth', planetLocation('Earth', T))
        print('Starman', planetLocation('Starman', T))
        print('Mercury', planetLocation('Mercury', T)) 
        print('Venus', planetLocation('Venus', T)) 
        print('Mars', planetLocation('Mars', T)) 

    pn = 0
    t = np.linspace(0, 2*pi, 100)
    orb = np.array([.25*np.cos(t), .25*np.sin(t)])
    fig, ax = plt.subplots()
    rot = 0
    T = Time.now()
    for p in planetNames:
        pLoc = planetLocation(p, T)
        pn = pLoc[4]
        orbit = np.array([pn*np.cos(t), pn*np.sin(t)])
        ax.plot( pLoc[2]+orbit[0,:], pLoc[3]+orbit[1,:] )
        ax.plot( pn*cos(rot+pLoc[0]) + pLoc[2] + orb[0,:], pn*sin(rot+pLoc[0]) + pLoc[3] + orb[1,:])
    ax.grid(color='lightgray',linestyle='--')
    ax.set_aspect('equal','box')
    fig.savefig('solar.png')
    exit(0)


    t = np.linspace(0, 2*pi, 100)
    earth = np.array([earth_radius*np.cos(t), earth_radius*np.sin(t)])  
    mars = np.array([mars_radius*np.cos(t), mars_radius*np.sin(t)])  
    sm = np.array([sm_arm*np.cos(t)+sm_epi*cos(sm_ang), sm_arm*np.sin(t)+sm_epi*sin(sm_ang)])
    fig, ax = plt.subplots()
    ax.plot( earth[0,:], earth[1,:] )
    ax.plot( mars[0,:], mars[1,:] )
    ax.plot( sm[0,:], sm[1,:] )
    ax.grid(color='lightgray',linestyle='--')
    ax.set_aspect('equal','box')
    fig.savefig('starman.png')
    exit(0)

if False:
    # Spicepy
    import math
    import spiceypy
    spiceypy.furnsh('../kernels/naif0012.tls')
    spiceypy.furnsh('../kernels/de432s.bsp')
    DATE_TODAY = datetime.today()
    DATE_TODAY = DATE_TODAY.strftime('%Y-%m-%dT00:00:00')
    ET_TODAY_MIDNIGHT = spiceypy.utc2et(DATE_TODAY)
    print(ET_TODAY_MIDNIGHT)
    EARTH_STATE_WRT_SUN, EARTH_SUN_LT = spiceypy.spkgeo(
            targ=399,
            et=ET_TODAY_MIDNIGHT,
            ref='ECLIPJ2000',
            obs=10)
    print(EARTH_STATE_WRT_SUN)
    EARTH_SUN_DISTANCE = math.sqrt(
            EARTH_STATE_WRT_SUN[0]**2.0 +
            EARTH_STATE_WRT_SUN[1]**2.0 +
            EARTH_STATE_WRT_SUN[2]**2.0)
    EARTH_SUN_DISTANCE_AU = spiceypy.convrt(EARTH_SUN_DISTANCE, 'km', 'AU')
    print('Earth to Sun distance in AU', EARTH_SUN_DISTANCE_AU)
    exit(0)
