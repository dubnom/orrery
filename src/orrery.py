from math import degrees, radians, sin, cos, floor, fmod, pi
from datetime import datetime, timedelta
from time import sleep
import os
import json
from json.decoder import JSONDecodeError
from threading import Thread, Event
from random import randint, random
from tic import TicController, T500_CURRENTS, t500_lookupCurrent, TicList
from settings import *
from usage import *


USAGE_WRITE_PERIOD = 5 * 60     # Number of seconds between file updates
USAGE_FILE_NAME = "usage.json"

STATE_FILENAME = "position.json"
STEPS_PER_ROTATION = 400 * 8
DAYS_IN_MERCURY_YEAR = 88
STEPS_PER_DAY = STEPS_PER_ROTATION / DAYS_IN_MERCURY_YEAR

planets = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

planetInfo = {
        'Mercury': (87.97, 0.448407, 5.05985, 0, 0, 1),
        'Venus': (224.7, 0.727912, 5.80397, 0, 0, 2),
        'Earth': (365.256, 0.986066, 2.38918, 0, 0, 3),
        # 'Starman': (557, .75+.98*3, 2.38918, .75*cos(sm_ang), .75*sin(sm_ang), 2.94 + .75),
        'Mars': (686.98, 1.59736, 3.67414, 0, 0, 4),
        'Jupiter': (4332.59, 5.42634, 3.85817, 0, 0, 5),
        'Saturn': (10755.7, 10.0658, 4.7359, 0, 0, 6),
        'Uranus': (30687.2, 19.8964, 0.479293, 0, 0, 7),
        'Neptune': (60190, 29.9449, 5.9957, 0, 0, 8),
        }

# The orrery supports simple circular orbits.
# The location of the planets (and Starman) can be calculated by taking a starting point,
# the 'epoch' and incorporating the orbital rate * elapsed time.
# StarMan requires an extra offset (x,y) to handle its offset from the sun.
epoch = datetime(2018,2,6)
def planetLocation(name, t):
    daysPerYear, radius, aOffset, xOffset, yOffset, pn = planetInfo[name]
    days = (t - epoch).days
    angle = radians(360*days/daysPerYear) + aOffset
    return degrees(angle % (2*pi)), radius, xOffset, yOffset, pn


class OrreryError(Exception):
    pass


class PersistentState():
    """
    The state of the orrery needs to be updated in persistent storage
    to allow it to recover if power is removed.

    mode -> 'now', 'travel', 'unknown'
    state -> 'stopped', 'moving', 'unknown'
    """
    
    state = None
    trust = False

    def __init__(self, fileName, position: float):
        self._fileName = fileName
        try:
            with open(self._fileName, 'r') as f:
                self.state = json.load(f)
                self.trust = True
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.set('now', 'stopped', position)

    def set(self, mode: str=None, state: str=None, position: float=-1):
        newState = {}
        newState['mode'] = mode if mode else self.state['mode']
        newState['state'] = state if state else self.state['state']
        newState['position'] = position if position != -1 else self.state['position']
        if self.state != newState:
            self.state = newState
            with open(self._fileName, 'w') as f:
                json.dump(self.state, f)
                f.flush()
                os.fsync(f.fileno())


class Orrery():
    """
    One rotation of the stepper motor is equal to one orbit of Mercury.
    Time is proportional to Earth orbit(s).
    Steps are proportional to Mercury orbits.
    One Mercury orbit = 400 * 8 steps
    One Mercury year = 88 Earth days
    One Earth day = 400 * 8 / 88 steps
    """

    _tic = None
    _targetPos = 0
    _targetT = _nowT = _demoEndT = _usageT = datetime.now()
    _demoDir = True

    def __init__(self, ticID=None):
        # Discover the ticID if nothing is specified
        if not ticID:
            tics = TicList()
            if len(tics) == 0:
                raise OrreryError("No TIC motor controller found.")
            elif len(tics) > 1:
                raise OrreryError("Too many TIC motor controllers found.")
            ticID = tics[0][0]
        
        self._tic = TicController(ticID)
        if not self._tic:
            raise OrreryError(f"TIC motor controller couldn't be found '{ticID}'")

        # Set up state
        position = self._prevPos = self._timeToPosition(datetime.utcnow())
        self._state = PersistentState(STATE_FILENAME, position)

        self._usage = Usage(USAGE_FILE_NAME)
        self._usage.add('restarts', 1)
        self._usage.save()

        # FIX: SET THE POSITION NO MATTER WHAT.
        # Power-up the tic, reset position if the state couldn't be trusted
        # if not self._state.trust:
        self._tic.haltAndSetPosition(int(position))
        self._ticThread = TicThread(self._tic, .1, self._updateOrreryPos)
        self._ticThread.start()
        self._tic.exitSafeStart()
        self._tic.energize()

        # Start the clock thread
        self._clockThread = ClockThread(1., self._updateNow)
        self._clockThread.start()

        # Settings
        self.applySettings()

    def applySettings(self):
        self._settings = Settings()
        self._tic.setMaxSpeed( self._settings.settings['maxSpeed'] )
        self._tic.setCurrentLimit( t500_lookupCurrent( self._settings.settings['current'] ))

    def getUsage(self):
        return self._usage

    def shutdown(self):
        self.halt()
        self.deenergize()
        self._usage.save()

    def _timeToPosition(self, t: datetime) -> float:
        td = t - datetime(1,1,1,0,0,0)
        jd = td.days + (td.seconds / 86400)
        return jd * STEPS_PER_DAY

    def _positionToTime(self, position: int) -> datetime:
        jd = position / STEPS_PER_DAY
        return datetime(1,1,1,0,0,0) + timedelta(jd)

    def _updateOrreryPos(self, orreryPos: float):
        steps = abs(self._prevPos-self._state.state['position'])
        self._usage.add('orrery_days', steps / STEPS_PER_DAY)
        self._prevPos = self._state.state['position']
        if int(self._state.state['position']) == int(self._targetPos):
            self._state.set(state='stopped', position=orreryPos)
        else:
            self._state.set(state='moving', position=orreryPos)

    def _setTime(self, targetT: datetime):
        self._targetT = targetT
        newPos = self._timeToPosition(targetT)
        if int(self._targetPos) != int(newPos):
            self._targetPos = newPos
            self.resume()

    def _updateNow(self, nowT: datetime):
        # Update usage, and save every so often
        elapsedSeconds = (nowT - self._nowT).total_seconds()
        self._usage.add('seconds_powered', elapsedSeconds)
        if (nowT - self._usageT).total_seconds() > USAGE_WRITE_PERIOD:
            self._usage.save()
            self._usageT = nowT

        # Do things based on the mode of the orrery
        self._nowT = nowT
        if self._state.state['mode'] == 'now':
            self._setTime(nowT)
        elif self._state.state['mode'] == 'demo':
            # Demo mode:
            #   randomly move forward or backward 1 planet year, and then
            #   return to the current time.  Continue until 'now'
            #   or time travel is requested.
            if self._state.state['state'] == 'stopped':
                if self._nowT > self._demoEndT:
                    self._state.state['mode'] = 'now'
                else:
                    if self._demoDir:
                        randomPlanet = planets[randint(0, len(planets)-1)]
                        direction = -1 if random() < .5 else 1
                        self.moveRelative(direction, randomPlanet)
                        self._state.state['mode'] = 'demo'
                    else:
                        self._setTime(self._nowT)
                    self._demoDir = not self._demoDir 

    def timeNow(self):
        self._state.set(mode='now')
        self._setTime(self._nowT)

    def timeTravel(self, targetT: datetime):
        self._state.set(mode='travel')
        self._setTime(targetT)

    def demoMode(self):
        self._demoEndT = self._nowT + timedelta(minutes=self._settings.settings['demo_time'])
        self._state.set(mode='demo')
        self._usage.add('demo_requests', 1)

    def planetPositions(self):
        if self._state.state['state'] == 'moving':
            T = self._positionToTime(self._state.state['position'])
        else:
            T = self._targetT

        positions = {}
        for planet in planets:
            pos = planetLocation(planet, T)
            positions[planet] = pos[0:2]

        timeStr = T.strftime('%b-%d-%Y %H:%M:%S')
        return {'positions': positions, 'time': timeStr, 'state': self._state.state}

    def status(self):
        results = self.planetPositions()
        results['status'] = {
                "op_state": (self._tic.getOperationState(), ''),
                "error_status": (self._tic.getErrorStatus(), ''),
                "max_speed": (self._tic.getMaxSpeed() / 10000, 'steps per second'),
                "vin": (round(self._tic.getVINVoltage(), 1), 'volts'),
                "cur_pos": (self._tic.getCurrentPosition(), 'steps'),
                "target_pos": (self._tic.getTargetPosition(), 'steps'),
                "current": (T500_CURRENTS[self._tic.getCurrentLimit()], 'amps'),
                }
        results['usage'] = self._usage.usage
        return results

    def halt(self):
        self._tic.haltAndHold()

    def deenergize(self):
        self._tic.deenergize()

    def resume(self):
        self._tic.clearDriverError()
        self._tic.exitSafeStart()
        self._tic.energize()
        self._tic.setTargetPosition(int(self._targetPos))

    def resetNow(self):
        position = self._timeToPosition(self._nowT)
        self._tic.haltAndSetPosition(int(position))
        self.timeNow()

    def moveRelative(self, amt, typ):
        if typ in planetInfo:
            pInfo = planetInfo[typ]
            steps = amt * STEPS_PER_DAY * pInfo[0]
        elif typ == 'Days':
            steps = STEPS_PER_DAY * amt
        else:
            steps = amt
        self.timeTravel( self._positionToTime( self._targetPos + steps ))


class TicThread(Thread):
    """Thread to continuously read the current position of the orrery."""

    def __init__(self, tic: TicController, seconds: float, callBack):
        Thread.__init__(self)
        self._tic = tic
        self._seconds = seconds
        self._callBack = callBack
        self._stopped = Event()

    def run(self):
        while not self._stopped.wait(self._seconds):
            orreryPos = self._tic.getCurrentPosition()
            self._callBack(orreryPos)

    def stop(self):
        self._stopped.set()


class ClockThread(Thread):
    """Thread used to update the orrery at some time interval"""

    def __init__(self, seconds: float, callBack):
        Thread.__init__(self)
        self._seconds = seconds
        self._callBack = callBack
        self._stopped = Event()

    def run(self):
        while not self._stopped.wait(self._seconds):
            nowT = datetime.now()
            if self._callBack:
                self._callBack(nowT)

    def stop(self):
        self._stopped.set()
