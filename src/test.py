from tach import Tach

interval = 5 

tach = Tach(17, interval)
tach.start()

while True:
    if tach.loop():
        print(tach.bps)

