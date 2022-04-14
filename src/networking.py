from string import Template

CONFIG_DIR = "config/"
conf_files = \
    [
        ("hostapd.conf",        "/etc/hostapd/"),
        ("wpa_supplicant.conf", "/etc/wpa_supplicant/"),
    ]

def networkConfig(params):
    for name, path in conf_files:
        with open(f'{CONFIG_DIR}{name}', 'r') as fileIn:
            tmp = Template(fileIn.read())
            with open(f'{path}{name}', 'w') as fileOut:
                fileOut.write(tmp.substitute(params))


