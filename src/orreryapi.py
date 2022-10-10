import requests


class OrreryClient:
    """Local client to send requests to the orrery server."""

    def __init__(self, url='http://localhost/api'):
        self._url = url

    def status(self):
        r = requests.get(f"{self._url}/status")
        return r.json()

    def move(self, amt, typ):
        params = {'amt': amt, 'typ': typ}
        r = requests.post(f"{self._url}/move", json=params)

    def halt(self):
        r = requests.post(f"{self._url}/halt")

    def deenergize(self):
        r = requests.post(f"{self._url}/deenergize")

    def resume(self):
        r = requests.post(f"{self._url}/resume")

    def resetNow(self):
        r = requests.post(f"{self._url}/resetnow")

    def timeNow(self):
        r = requests.post(f"{self._url}/timeNow")

    def timeTravel(self, timeString):
        params = {"time_string": timeString}
        r = requests.post(f"{self._url}/timeTravel", json=params)

    def demo(self):
        r = requests.post(f"{self._url}/demo")

    def reboot(self):
        r = requests.post(f"{self._url}/reboot")

    def swupdate(self):
        r = requests.post(f"{self._url}/swupdate")
