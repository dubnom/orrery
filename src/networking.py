import os
import re
from string import Template

SAFE_HOSTNAME = re.compile('^[a-zA-Z0-9\\.\\-]{1,}$')
CONFIG_DIR = "config/"
conf_files = \
    [
        ("hostapd.conf",        "/etc/hostapd/"),
        ("wpa_supplicant.conf", "/etc/wpa_supplicant/"),
    ]

def networkConfig(params):
    # Use templates to update various config files
    for name, path in conf_files:
        with open(f'{CONFIG_DIR}{name}', 'r') as fileIn:
            tmp = Template(fileIn.read())
            with open(f'{path}{name}', 'w') as fileOut:
                fileOut.write(tmp.substitute(params))

    # Hostname is updated using the command line
    # and made safe through the regular expression
    match = SAFE_HOSTNAME.match(params["hostname"])
    if match and len(match.group()) > 0 and not match.group().startswith('-'):
        os.system('hostname %s' % match.group())