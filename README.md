# Orrery
An orrery is a mechanical simulation of our solar system.  This project is for a particular orrery,
that we designed and built, which uses a stepper motor to turn the orbits of the planets.  The software
is designed to run on a Raspberry Pi and use Pololu stepper motor controllers.

Since the ratio between
planetary orbits must be nearly identical between various orreries, this project can easily be adapted to
operate any stepper motor driven orrery on any platform.

Our orrery has the stepper motor driving the orbit of Mercury - one full rotation of the stepper is equal to one
Mercury year (one full rotation of Mercury).  Mercury takes roughly 88 Earth days to complete an orbit.

# Dynamic Web Interface
The web interface allows users to -
* See the position of the planets
* Set a date in the future or past to travel to
* Return to today
* Run a demo which moves planets forward and back randomly
* Incrementally move the solar system by various planet days and years
* Configure the network (Raspberry Pi)
* Update the codebase
