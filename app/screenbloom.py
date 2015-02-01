from PIL import ImageGrab
from rgb_cie import Converter
from beautifulhue.api import Bridge
import ssdp
import time
from datetime import datetime
import urllib2
import colorsys
import os


class Screen(object):
    def __init__(self, hex_color, bridge, ip, devicename, bulbs, sat, bri, transition):
        self.hex_color = hex_color
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.sat = sat
        self.bri = bri
        self.transition = transition

converter = Converter()  # Class for easy conversion of RGB to Hue CIE


def initialize(config):
    ip = config[0]
    devicename = config[1]
    bulbs = config[2]
    sat = config[3]
    bri = config[4]
    transition = config[5]

    bridge = Bridge(device={'ip': ip}, user={'name': devicename})
    screen = Screen('#FFFFFF', bridge, ip, devicename, bulbs, sat, bri, transition)

    return screen

# ssdp_response = ssdp.discover('IpBridge')
# hue_ip = str(ssdp_response)[22:33]
#screen = Screen('#FFFFFF', [])


def update_bulb(screen, cie_color, hex_color):
    """ Updates Hue bulb to specified CIE value """
    if hex_color == screen.hex_color:
        print 'Color is the same, no update necessary.'
        pass
    else:
        bulbs = [2, 3]
        screen.hex_color = hex_color
        print 'Updating color...'

        for bulb in bulbs:
            resource = {
                'which': bulb,
                'data': {
                    'state': {
                        'xy': cie_color,
                        'sat': 255,
                        'bri': 254,
                        'transitiontime': 12
                    }
                }
            }

            screen.bridge.light.update(resource)


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
    loop_start = datetime.now()
    for x in range(width / 2):
        for y in range(height / 2):
            cpixel = pixels[x, y]
            data.append(cpixel)
    loop_end = datetime.now()
    loop_time = loop_end - loop_start
    #print 'First loop took %s microseconds' % loop_time.microseconds

    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    # If alpha is greater than 200/255 (non-transparent), add it to the average
    loop_start = datetime.now()
    for x in range(len(data)):
        try:
            if data[x][3] > 200 / 255:
                r += data[x][0]
                g += data[x][1]
                b += data[x][2]
        except IndexError:
            r += data[x][0]
            g += data[x][1]
            b += data[x][2]

        counter += 1
    loop_end = datetime.now()
    loop_time = loop_end - loop_start
    #print 'Second loop took %s microseconds' % loop_time.microseconds

    # Compute average RGB values
    r_avg = r / counter
    g_avg = g / counter
    b_avg = b / counter

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color
    }

    return data