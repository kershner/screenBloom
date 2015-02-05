from PIL import ImageGrab
from rgb_cie import Converter
from beautifulhue.api import Bridge
import requests
# import ssdp
# from datetime import datetime
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


# Check server status
def check_server(host):
    try:
        r = requests.get('http://%s:5000/new-user' % host)
        response = r.status_code
    except requests.ConnectionError:
        response = 404
    if response == 200:
        return True
    else:
        return False


# Return properly formatted list from config.txt
def config_to_list():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open('%s/config.txt' % current_path, 'r') as config_file:
        config = '\n'.join(config_file).split()

    return config


# Rewrite config file with given arguments
def write_config(sat, bri, trans, running, user_exit):
    current_path = os.path.dirname(os.path.abspath(__file__))
    config = config_to_list()

    with open('%s/config.txt' % current_path, 'w+') as config_file:
        config_file.write(config[0] + '\n')
        config_file.write(config[1] + '\n')
        config_file.write(config[2] + '\n')
        config_file.write(sat + '\n')
        config_file.write(bri + '\n')
        config_file.write(trans + '\n')
        config_file.write(running + '\n')
        config_file.write(user_exit)


# Grab attributes for screen instance
def initialize():
    config = config_to_list()

    ip = config[0]
    devicename = config[1]
    bulbs = ''.join(config[2]).split(',')
    bulbs = [int(i) for i in bulbs]
    sat = int(config[3])
    bri = int(config[4])
    transition = int(config[5])
    bridge = Bridge(device={'ip': ip}, user={'name': devicename})

    attributes = ('#FFFFFF', bridge, ip, devicename, bulbs, sat, bri, transition)

    return attributes


# Get updated attributes, re-initialize screen object
def re_initialize():
    # Attributes
    at = initialize()

    global screen
    screen = Screen(at[0], at[1], at[2], at[3], at[4], at[5], at[6], at[7])


def get_brightness(dark_pixel_ratio):
    brightness = 254
    max_brightness = 254
    min_brightness = 50

    if dark_pixel_ratio >= 40.0:
        brightness -= (dark_pixel_ratio * max_brightness) / 100
        brightness += 50
        if brightness < min_brightness:
            brightness = min_brightness

    return brightness


def update_bulb(screen_obj, cie_color, hex_color, dark_ratio):
    """ Updates Hue bulb to specified CIE value """
    dark_ratio = get_brightness(dark_ratio)

    if hex_color == screen.hex_color:
        print 'Color is the same, no update necessary.'
        pass
    else:
        bulbs = screen_obj.bulbs
        screen_obj.hex_color = hex_color
        print 'Updating color to %s...' % hex_color

        for bulb in bulbs:
            resource = {
                'which': bulb,
                'data': {
                    'state': {
                        'xy': cie_color,
                        'sat': screen_obj.sat,
                        #'bri': screen_obj.bri,
                        'bri': dark_ratio,
                        'transitiontime': screen_obj.transition
                    }
                }
            }

            screen.bridge.light.update(resource)


def update_bulb_default():
    """ Set bulbs to a standard white color """
    print 'Setting bulbs to default'
    bulbs = screen.bulbs

    for bulb in bulbs:
            resource = {
                'which': bulb,
                'data': {
                    'state': {
                        'xy': [0.33618074375880236, 0.36036963628407426],
                        'sat': screen.sat,
                        'bri': screen.bri,
                        'transitiontime': screen.transition
                    }
                }
            }

            screen.bridge.light.update(resource)


def tup_to_hex(rgb_tuple):
    """ Convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


def screen_avg():
    """ Grabs screenshot of current window, returns avg color values of all pixels """
    # Grab image of current screen
    img = ImageGrab.grab()

    # Resize image so it's faster to process
    size = (32, 32)
    img = img.resize(size)

    # Create list of pixels
    pixels = list(img.getdata())

    black_pixels = 0
    total_pixels = 0
    r = 0
    g = 0
    b = 0
    counter = 0

    for x in range(len(pixels)):
        try:
            # Ignore black pixels
            if pixels[x][0] < 70 and pixels[x][1] < 70 and pixels[x][2] < 70:
                black_pixels += 1
                total_pixels += 1
            # Ignore transparent pixels
            elif pixels[x][3] > 200 / 255:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
                total_pixels += 1
        # In case pixel doesn't have an alpha channel
        except IndexError:
            r += pixels[x][0]
            g += pixels[x][1]
            b += pixels[x][2]
            total_pixels += 1

        counter += 1

    # Compute average RGB values
    try:
        r_avg = r / counter
        g_avg = g / counter
        b_avg = b / counter
    # Will divide by zero if mostly black pixels in image, if so set to default value
    except ZeroDivisionError:
        r_avg = 230
        g_avg = 230
        b_avg = 230

    dark_ratio = (float(black_pixels) / float(total_pixels)) * 100
    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    # print 'Black Pixels: ', black_pixels
    # print 'Total Pixels: ', total_pixles
    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color,
        'dark_ratio': dark_ratio
    }

    return data


def run():
    # Get avg color of current screen
    results = screen_avg()

    try:
        # Update Hue bulbs to avg color of screen
        update_bulb(screen, results['hue_color'], results['screen_hex'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass

atr = initialize()
converter = Converter()  # Class for easy conversion of RGB to Hue CIE
screen = Screen(atr[0], atr[1], atr[2], atr[3], atr[4], atr[5], atr[6], atr[7])
# ssdp_response = ssdp.discover('IpBridge')
# hue_ip = str(ssdp_response)[22:33]
# screen = Screen('#FFFFFF', [])