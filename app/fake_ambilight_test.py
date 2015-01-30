from PIL import ImageGrab
from rgb_cie import Converter
import ssdp
from beautifulhue.api import Bridge
import time
import urllib2

ssdp_response = ssdp.discover('IpBridge')
hue_ip = str(ssdp_response)[22:33]

bridge = Bridge(device={'ip': hue_ip}, user={'name': 'tylerkershner'})
converter = Converter()  # Class for easy conversion of RGB to Hue CIE


def update_bulb(bulb, cie_color):
    """ Updates Hue bulb to specified CIE value """
    resource = {
        'which': bulb,
        'data': {
            'state': {
                'xy': cie_color,
                'sat': 220
            }
        }
    }

    bridge.light.update(resource)


def tup_to_hex(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


def screen_avg():
    """ Grabs screenshot of current window, returns avg RGB of all pixels """
    print 'Firing screen_avg()...'
    img = ImageGrab.grab()

    # Grab width and height
    width, height = img.size

    # Make list of all pixels
    pixels = img.load()
    data = []
    for x in range(width):
        for y in range(height):
            cpixel = pixels[x, y]
            data.append(cpixel)

    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    # If alpha is greater than 200/255 (non-transparent), add it to the average
    for x in range(len(data)):
        try:
            if data[x][3] > 200:
                r += data[x][0]
                g += data[x][1]
                b += data[x][2]
        except IndexError:
            r += data[x][0]
            g += data[x][1]
            b += data[x][2]

        counter += 1

    # Compute average RGB values
    r_avg = r / counter
    g_avg = g / counter
    b_avg = b / counter

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])

    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color
    }

    return data

if __name__ == '__main__':
    while True:
        screen = screen_avg()
        try:
            update_bulb(2, screen['hue_color'])
            update_bulb(3, screen['hue_color'])
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass
        print screen['screen_hex']
        time.sleep(0.70)
