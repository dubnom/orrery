#!/usr/bin/python3
from bottle import route, get, post, default_app, run, static_file, request, redirect
import socket
import logging
import json
import os
import dateparser
from pytz import all_timezones
import networking
from orrery import Orrery
from settings import *


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.ERROR)

@route('/')
@route('/orrery')
def redirection():
    return redirect('/orrery.html')

@route('/admin')
def redirection():
    return redirect('/admin.html')

@route('/expert')
def redirection():
    return redirect('/expert.html')

@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='data')

@route('/images/<filename>')
def server_static(filename):
    return static_file(filename, root='images')

@route('/<filename:re:.*\\.html>')
@route('/data/<filename>')
@route('/<filename:re:.*\\.css>')
@route('/<filename:re:.*\\.js>')
def server_static(filename):
    return static_file(filename, root='data')

@route('/fonts/<filename:re:.*\\.woff.*>')
def server_static(filename):
    return static_file(filename, root='data/fonts')

@get('/countries')
@post('/countries')
def get_countries():
    from pycountry import countries
    return json.dumps([(c.alpha_2,c.name) for c in countries])

@get('/timezones')
@post('/timezones')
def get_timezones():
    return json.dumps(all_timezones)

@get('/api/planetPositions')
@post('/api/planetPositions')
def getPlanetPositions():
    return json.dumps(orrery.planetPositions())

@get('/api/status')
@post('/api/status')
def getStatus():
    return json.dumps(orrery.status())

@post('/api/move')
def move():
    amt = request.json['amt']
    typ = request.json['typ']
    orrery.moveRelative(amt, typ)
    return json.dumps({})

@get('/api/halt')
@post('/api/halt')
def halt():
    orrery.halt()
    return json.dumps({})

@get('/api/deenergize')
@post('/api/deenergize')
def halt():
    orrery.deenergize()
    return json.dumps({})

@get('/api/resume')
@post('/api/resume')
def resume():
    orrery.resume()
    return json.dumps({})

@get('/api/resetnow')
@post('/api/resetnow')
def resetNow():
    orrery.resetNow()
    return json.dumps({})

@get('/api/reboot')
@post('/api/reboot')
def reboot():
    os.system('reboot')
    return json.dumps({})

@get('/api/getsettings')
@post('/api/getsettings')
def getSettings():
    return json.dumps(Settings().settings)

@post('/api/setsettings')
def setSettings():
    params = request.json['settings']
    Settings().set(params) 
    orrery.applySettings()
    networking.networkConfig(params)
    return json.dumps({})

@post('/api/timeNow')
def timeNow():
    orrery.timeNow()
    return json.dumps({})


@post('/api/timeTravel')
def timeTravel():
    timeStr = request.json['time_string']
    timeDT = dateparser.parse(timeStr, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    orrery.timeTravel(timeDT)
    return json.dumps({})


if __name__ == "__main__":
    orrery = Orrery()
    try:
        run(host='0.0.0.0',port=80,debug=True)
    finally:
        orrery.halt()
        orrery.deenergize()
