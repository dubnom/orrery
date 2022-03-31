import netifaces

IFNAME = 'wlan0'

MAC = str(netifaces.ifaddresses(IFNAME)[netifaces.AF_LINK][0]['addr'])
hx = MAC.split(':')

networkName = f'orrery{hx[4:]}' 

