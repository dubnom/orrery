#!/usr/bin/python3
from bottle import route, get, post, default_app, run, static_file, request, redirect
import socket
import logging
import json
import dateparser
from orrery import Orrery

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.ERROR)

@route('/')
def redirection():
    return redirect('/orrery/src/data/orrery.html')

@route('/admin')
def redirection():
    return redirect('/orrery/src/data/admin.html')

@route('/images/<filename>')
@route('/orrery/src/images/<filename>')
def server_static(filename):
    return static_file(filename, root='images')

@route('/data/<filename>')
@route('/<filename:re:.*\\.css>')
@route('/<filename:re:.*\\.js>')
@route('/orrery/src/data/<filename>')
@route('/orrery/src/<filename:re:.*\\.css>')
@route('/orrery/src/<filename:re:.*\\.js>')
def server_static(filename):
    return static_file(filename, root='data')

@route('/fonts/<filename:re:.*\\.woff>')
def server_static(filename):
    print(filename)
    return static_file(filename, root='data/fonts')

@get('/orrery/api/planetPositions')
@post('/orrery/api/planetPositions')
def getPlanetPositions():
    return json.dumps(orrery.planetPositions())

@get('/orrery/api/status')
@post('/orrery/api/status')
def getStatus():
    return json.dumps(orrery.status())

@post('/orrery/api/move')
def move():
    amt = request.json['amt']
    typ = request.json['typ']
    orrery.moveRelative(amt, typ)
    return json.dumps({})

@get('/orrery/api/halt')
@post('/orrery/api/halt')
def halt():
    orrery.halt()
    return json.dumps({})

@get('/orrery/api/deenergize')
@post('/orrery/api/deenergize')
def halt():
    orrery.deenergize()
    return json.dumps({})

@get('/orrery/api/resume')
@post('/orrery/api/resume')
def resume():
    orrery.resume()
    return json.dumps({})

@get('/orrery/api/resetnow')
@post('/orrery/api/resetnow')
def resetNow():
    orrery.resetNow()
    return json.dumps({})

@get('/orrery/api/getsettings')
@post('/orrery/api/getsettings')
def getSettings():
    return json.dumps(orrery.settings.settings)

@post('/orrery/api/setsettings')
def setSettings():
    orrery.settings.set(request.json['settings'])
    return json.dumps({})

@post('/orrery/api/timeNow')
def timeNow():
    orrery.timeNow()
    return json.dumps({})


@post('/orrery/api/timeTravel')
def timeTravel():
    timeStr = request.json['time_string']
    timeDT = dateparser.parse(timeStr, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    orrery.timeTravel(timeDT)
    return json.dumps({})


if __name__ == "__main__":
    orrery = Orrery()
    try:
        run(host='0.0.0.0',port=8080,debug=True)
    finally:
        orrery.halt()
        orrery.deenergize()
