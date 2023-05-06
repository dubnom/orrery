import json
from json.decoder import JSONDecodeError
form copy import copy
import netifaces

SETTINGS_FILENAME = "settings.json"

# Determine the default access point ssid based on the MAC address
IFNAME = 'wlan0'
MAC = str(netifaces.ifaddresses(IFNAME)[netifaces.AF_LINK][0]['addr'])
hx = ''.join(MAC.split(':'))
ap_ssid = f'orrery{hx[8:]}' 

defaults = { 
    'demo_time': 5,
    'maxSpeed': 32000000,
    'current': .495,
    'hold_current': .2,
    'wifi_mode': 'server',
    'wifi_country': 'US',
    'ap_ssid': ap_ssid,
    'ap_pass': 'youranus',
    'ap_channel': 10,
    'client_ssid': '',
    'client_pass': '',
    'hostname': 'orrery',
}

class Settings():
    """
    Application settings.
    """

    def __init__(self, fileName=SETTINGS_FILENAME):
        self._fileName = fileName
        self.settings = copy(defaults)
        try:
            with open(self._fileName, 'r') as f:
                self.settings.update(json.load(f))
        except (FileNotFoundError, JSONDecodeError):
            pass

    def reset(self):
        self.set(copy(defaults))

    def set(self, settings):
        self.settings.update(settings)
        self._save()

    def _save(self):
        with open(self._fileName, 'w') as f:
            json.dump(self.settings, f)
            f.flush()
