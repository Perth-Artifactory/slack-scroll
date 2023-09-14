"""
Twittinator ESP32 script start
"""

from MicroWebSrv2 import *
from time import sleep


@WebRoute(GET, '/new_message', name='New Message')
def RequestTestPost(microWebSrv2, request):
    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>New Message</title>
        </head>
        <body>
            <h2>Twittinator - New Message</h2>
            User address: %s<br />
            <form action="/new_message" method="post">
                Message: <input type="text" name="message"><br />
                Formatting:  <input type="text" name="formatting"><br />
                <input type="submit" value="OK">
            </form>
        </body>
    </html>
    """ % request.UserAddress[0]
    request.Response.ReturnOk(content)


# ------------------------------------------------------------------------

@WebRoute(POST, '/new_message', name='New Message Posted')
def RequestTestPost(microWebSrv2, request):
    data = request.GetPostedURLEncodedForm()
    try:
        message = data['message']
        formatting = data['formatting']
    except:
        request.Response.ReturnBadRequest()
        return
    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>New Message Posted</title>
        </head>
        <body>
            <h2>Twittinator - New Message Posted</h2>
            Message '%s' (%s)<br />
        </body>
    </html>
    """ % (MicroWebSrv2.HTMLEscape(message),
           MicroWebSrv2.HTMLEscape(formatting))
    request.Response.ReturnOk(content)


# ============================================================================
# ============================================================================
# ============================================================================

print()

# Instanciates the MicroWebSrv2 class,
mws2 = MicroWebSrv2()

# Blake 2020-08-09 set root path for ESP32
mws2.RootPath = '/www/'

# For embedded MicroPython, use a very light configuration,
mws2.SetEmbeddedConfig()

# All pages not found will be redirected to the home '/',
mws2.NotFoundURL = '/'

# Starts the server as easily as possible in managed mode,
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

# ============================================================================
# ============================================================================
# ============================================================================
