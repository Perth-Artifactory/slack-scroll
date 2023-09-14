# from https://www.rototron.info/raspberry-pi-esp32-micropython-web-server-tutorial/
# modified for MicroWebSrv2

from time import sleep
from MicroWebSrv2 import *
from machine import Pin
from neopixel import NeoPixel
import json

np = NeoPixel(Pin(13), 1)


@WebRoute(POST, '/led')
def RequestLedGet(microWebSrv2, request):
    content = request.Content  # Read JSON color data
    colors = json.loads(content)
    blue, green, red = [colors[k] for k in sorted(colors.keys())]
    np[0] = (red, green, blue)
    np.write()
    response = request.Response
    response.ReturnOk()


mws2 = MicroWebSrv2()

# For embedded MicroPython, use a very light configuration,
mws2.SetEmbeddedConfig()

# Blake 2020-08-09 set root path for ESP32
mws2.RootPath = '/www/'

mws2.StartManaged()

# Main program loop until keyboard interrupt,
try:
    while mws2.IsRunning:
        sleep(1)
except KeyboardInterrupt:
    pass

# End,
print()
mws2.Stop()
print('Bye')
print()
