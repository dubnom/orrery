#!/usr/bin/python3
from gpiozero import Button
from settings import Settings
from networking import *


settings = Settings()

# Check the special reset button on the Orrery
button = Button(26)
if button.is_pressed:
    settings.reset()
    networkConfig(settings.settings)

# Return 1 if the access point should be started
# Return 0 to leave as a client
exit(settings.settings['wifi_mode'] == 'server')
