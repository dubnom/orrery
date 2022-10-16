#!/usr/bin/python3
from gevent import monkey; monkey.patch_all()
from bottle import route, get, post, default_app, run, static_file, request, redirect, Bottle
import socket
import logging
import json
import time
import os
import dateparser
from pytz import all_timezones
import networking
from orrery import Orrery
from settings import *


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.ERROR)
app = Bottle()

@app.route('/')
@app.route('/orrery')
def redirection():
    return redirect('/orrery.html')

@app.route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='data')

@app.route('/images/<filename>')
def server_static(filename):
    return static_file(filename, root='images')

@app.route('/<filename:re:.*\\.html>')
@app.route('/data/<filename>')
@app.route('/<filename:re:.*\\.css>')
@app.route('/<filename:re:.*\\.js>')
def server_static(filename):
    return static_file(filename, root='data')

@app.route('/fonts/<filename:re:.*\\.woff.*>')
def server_static(filename):
    return static_file(filename, root='data/fonts')

@app.get('/countries')
@app.post('/countries')
def get_countries():
    from pycountry import countries
    return json.dumps([(c.alpha_2,c.name) for c in countries])

@app.get('/timezones')
@app.post('/timezones')
def get_timezones():
    return json.dumps(all_timezones)

@app.get('/api/planetPositions')
@app.post('/api/planetPositions')
def getPlanetPositions():
    return json.dumps(orrery.planetPositions())

@app.get('/api/status')
@app.post('/api/status')
def getStatus():
    return json.dumps(orrery.status())

@app.post('/api/move')
def move():
    amt = request.json['amt']
    typ = request.json['typ']
    orrery.moveRelative(amt, typ)
    return json.dumps({})

@app.get('/api/demo')
@app.post('/api/demo')
def demo():
    orrery.demoMode()
    return json.dumps({})

@app.get('/api/halt')
@app.post('/api/halt')
def halt():
    orrery.halt()
    return json.dumps({})

@app.get('/api/deenergize')
@app.post('/api/deenergize')
def halt():
    orrery.deenergize()
    return json.dumps({})

@app.get('/api/resume')
@app.post('/api/resume')
def resume():
    orrery.resume()
    return json.dumps({})

@app.get('/api/resetnow')
@app.post('/api/resetnow')
def resetNow():
    orrery.resetNow()
    return json.dumps({})

@app.get('/api/reboot')
@app.post('/api/reboot')
def reboot():
    orrery.shutdown()
    os.system('reboot')
    return json.dumps({})

@app.get('/api/shutdown')
@app.post('/api/shutdown')
def shutdown():
    orrery.shutdown()
    os.system('shutdown -h now')
    return json.dumps({})

@app.get('/api/swupdate')
@app.post('/api/swupdate')
def swupdate():
    orrery.shutdown()
    os.system("git pull")
    os.system('reboot')
    return json.dumps({})

@app.get('/api/usage')
@app.post('/api/usage')
def usage():
    return json.dumps(orrery.getUsage().usage)

@app.get('/api/getsettings')
@app.post('/api/getsettings')
def getSettings():
    return json.dumps(Settings().settings)

@app.post('/api/setsettings')
def setSettings():
    params = request.json['settings']
    Settings().set(params) 
    orrery.applySettings()
    networking.networkConfig(Settings().settings)
    #timezone = Settings().settings[timezone]
    #if timezone in all_timezones:
    #    os.system(f'timedatectl set-timezone {timezone}');
    return json.dumps({})

@app.post('/api/timeNow')
def timeNow():
    orrery.timeNow()
    return json.dumps({})

@app.post('/api/timeTravel')
def timeTravel():
    timeStr = request.json['time_string']
    timeDT = dateparser.parse(timeStr, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    orrery.timeTravel(timeDT)
    return json.dumps({})

@app.route('/websocket/status')
def websock():
    logging.warning('WEBSOCKET begins!')
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')

    try:
        while True:
            status = orrery.status()
            ws.send(json.dumps(status))
            time.sleep(.25 if status['state']['state'] == 'moving' else 1)
    except WebSocketError:
        pass


if __name__ == "__main__":
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketError
    from geventwebsocket.handler import WebSocketHandler
    orrery = Orrery()
    try:
        server = WSGIServer(("0.0.0.0", 80), app, handler_class=WebSocketHandler)
        server.serve_forever()
    finally:
        orrery.halt()
        orrery.deenergize()
