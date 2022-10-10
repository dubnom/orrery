from gpiozero import Button
import logging
from orreryapi import *


# Setup logging
logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO)

# Setup the orrery client and the button to wait for
client = OrreryClient(url='http://localhost/api')
button = Button(22, pull_up=False, hold_repeat=False)

# Main loop
while True:
    logging.info("Waiting")
    button.wait_for_press()
    button.wait_for_release()
    logging.info("Demo Requested")
    client.demo()

