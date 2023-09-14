# from https://www.rototron.info/raspberry-pi-esp32-micropython-web-server-tutorial/
# modified for MicroWebSrv2

from time import sleep
from MicroWebSrv2 import *
from machine import Pin
from dht import DHT22

sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))  # DHT-22 on GPIO 15


@WebRoute(GET, '/dht')
def RequestDHTGet(microWebSrv2, request):
    try:
        sensor.measure()  # Poll sensor
        t, h = sensor.temperature(), sensor.humidity()
        if all(isinstance(i, float) for i in [t, h]):  # Confirm values
            data = '{0:.1f}&deg;C {1:.1f}%'.format(t, h)
        else:
            data = 'Invalid reading.'
    except:
        data = 'Attempting to read sensor...'

    content = 'data: {0}\n\n'.format(data)
    response = request.Response
    response.SetHeader('Cache-Control', 'no-cache')
    response.SetHeader('Content-Type', 'text/event-stream')
    # response.SetHeader('Content-Type', 'text/event-stream; charset=UTF-8')
    # contentType = 'text/event-stream',
    # contentCharset = 'UTF-8',
    response.ReturnOk(content)


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
