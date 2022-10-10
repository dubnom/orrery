from gpiozero import Button
from signal import pause
import time
from datetime import datetime, timedelta
import requests
from threading import Thread
import logging
import csv
from sys import argv
from random import randint
from orreryapi import *


# Constants
INTERVAL = 5        # Tach sampling seconds
BPS_CUTOFF = 22     # Minimum number of beats (teeth) per second for running
ACCEL_SECONDS = 10  # Acceleration time in seconds
DECEL_SECONDS = 15  # Deceleration time in seconds

planetNames = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]


# Setup logging
logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO)


def randomPlanetName():
    return planetNames[randint(0, len(planetNames)-1)]


class Tach(Thread):
    """Thread to monitor an optical encoder and track the number of blips per second (BPS)"""

    def __init__(self, pin, interval=60):
        Thread.__init__(self, daemon=True)
        self._pin = pin
        self._interval = interval

        # Optical encoder
        self.but = Button(pin, pull_up=True, bounce_time=.01)
        self.but.when_pressed = self._pressed
        self.but.when_released = self._released

        # Private working statistics
        self._st = None
        self._count = 0

        # Public statistics
        self.bps = 0
        self.count = 0

    def _pressed(self):
        self._count += 1

    def _released(self):
        pass

    def _reset(self):
        self._st = time.monotonic()
        self._count = 0

    def loop(self):
        if self._st == None:
            self._reset()
        t = time.monotonic()
        dt = t - self._st
        if dt >= self._interval:
            self.bps = self._count / self._interval
            self.count = self._count
            self._reset()
            return True
        return False

    def run(self):
        pause()


def main(amt, typ, note):
    startTime = datetime.now()
    logging.info("Starting")
    
    state_finish_time = None
    direction = -1
    orbitCount = 0

    logging.info("Connecting to orrery.")
    orrery = OrreryClient()

    logging.info("Starting tachometer.")
    tach = Tach(17, INTERVAL)
    tach.start()

    try:
        state = 'unknown'
        old_state = 'unknown'
        while state != 'exit':
            if tach.loop() or state != old_state:
                # Finite state machine to run the orrery
                old_state = state
                status = orrery.status()
                target_pos = status['status']['target_pos'][0]
                cur_pos = status['status']['cur_pos'][0]
                max_speed = status['status']['max_speed'][0]
                time_to_go = abs(target_pos - cur_pos) / max_speed

                logging.info(f"Orbit: {orbitCount}  State: {state}  Tach: {tach.count}, {tach.bps}  Pos: {cur_pos}, {target_pos}  Seconds left: {time_to_go}")
                with open("tach.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now().ctime(), orbitCount, state, tach.count, tach.bps, cur_pos, target_pos, time_to_go])

                if cur_pos == target_pos:
                    state = 'stopped'

                if state is 'stopped':
                    direction *= -1
                    planetName = randomPlanetName() if typ == 'Random' else typ
                    orrery.move(direction*amt, planetName)
                    if orbitCount:
                        logging.info(f"Orbit {orbitCount} completed.")
                    orbitCount += 1
                    logging.info(f"Starting orbit {orbitCount} {planetName}.")
                    state_finish_time = time.monotonic() + ACCEL_SECONDS
                    state = 'accelerating'
                elif state is 'accelerating':
                    if tach.bps > BPS_CUTOFF:
                        state = 'running'
                    elif time.monotonic() > state_finish_time:
                        state = 'exit'
                elif state is 'decelerating':
                    if status['state']['state'] == 'stopped':
                        state = 'stopped'
                    elif tach.bps > BPS_CUTOFF:
                        state_finish_time += INTERVAL
                    elif time.monotonic() > state_finish_time:
                        state = 'exit'
                elif state is 'running':
                    if time_to_go < DECEL_SECONDS:
                        state_finish_time = time.monotonic() + DECEL_SECONDS
                        state = 'decelerating'
                    elif tach.bps <= BPS_CUTOFF:
                        state = 'exit'
                elif state is 'unknown':
                    if status['state']['state'] != 'stopped':
                        orrery.resetNow()
                    state = 'stopped'

            time.sleep(.1)
    finally:
        # Log what we've accomplished
        endTime = datetime.now()
        delta = endTime - startTime
        logging.info(f"Started: {startTime}  Ended: {endTime}  Delta: {delta}  Orbits: {orbitCount}")

        # Append the statistics to a CSV file
        with open("stats.csv", "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([startTime.ctime(), delta.total_seconds(), orbitCount, amt, typ, note])

        # Turn off the orrery
        orrery.halt()
        orrery.deenergize()


if __name__ == '__main__':
    main(1, 'Random', ' '.join(argv[1:]))

