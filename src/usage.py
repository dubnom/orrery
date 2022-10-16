import json
from json.decoder import JSONDecodeError
from datetime import datetime


defaults = {
    'seconds_powered': 0.,
    'orrery_days': 0.,
    'demo_requests': 0,
    'started': None,
    'updated': None,
    'restarts': 0,
}


class Usage():
    """
    Class used to handle the tracking of orrery usage -
        - Amount of time powered on
        - Number of orrery days in motion
        - Number of demo requests
        - Start of data collection
        - Last time the usage was updated
    """

    def __init__(self, fileName):
        self._fileName = fileName
        try:
            with open(self._fileName, 'r') as f:
                self.usage = json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            defaults['started'] = str(datetime.now())
            self.usage = defaults
            self.save()

    def add(self, field, amount):
        self.usage[field] += amount

    def save(self):
        self.usage['updated'] = str(datetime.now())
        with open(self._fileName, 'w') as f:
            json.dump(self.usage, f)
            f.flush()
