from PIL import ImageGrab
from rgb_cie import Converter
from beautifulhue.api import Bridge
# from datetime import datetime
import requests
import threading
import urllib2
import colorsys
import webbrowser
import os
import time
import json


# Class for the start-up process
class StartupThread(threading.Thread):
    def __init__(self, host):
        super(StartupThread, self).__init__()
        self.stoprequest = threading.Event()
        self.host = host

    def run(self):
        if not self.stoprequest.isSet():
            # Check if config file has been created yet
            config_exists = os.path.isfile('config.txt')
            if config_exists:
                print 'Config already exists'
                # Wait for 200 status code from server then load up interface
                while not check_server(self.host):
                    time.sleep(0.2)
                # If the 'user_exit' value is False, app previously ended without being recorded
                # So we will set the 'running' value to False
                config = config_to_list()
                if config[7] == 'False':
                    running = 'False'
                    write_config(config[2], config[3], config[4], config[5], running, config[7])

                global atr, screen

                # Grab attributes from config file
                atr = initialize()

                # Initialize screen object
                screen = Screen(atr[0], atr[1], atr[2], atr[3], atr[4], atr[5], atr[6], atr[7])

                url = 'http://%s:5000/' % self.host
                webbrowser.open(url)
            else:
                # Config file doesn't exist, open new user interface
                print 'Config does not exist yet!'
                url = 'http://%s:5000/new-user' % self.host
                webbrowser.open(url)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StartupThread, self).join(timeout)


# Class for running ScreenBloom thread
class ScreenBloomThread(threading.Thread):
    def __init__(self, transition):
        super(ScreenBloomThread, self).__init__()
        self.transition = transition
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.isSet():
            run()

            transition = (float(self.transition) / 10) + 0.2
            time.sleep(transition)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloomThread, self).join(timeout)


# Class for Screen object to hold values during runtime
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


def print_hue_config():
    temp_bridge = Bridge(device={'ip': '192.168.0.2'}, user={'name': 'tylerkershner'})
    resource = {'which': 'bridge'}

    result = temp_bridge.config.get(resource)
    print json.dumps(result, sort_keys=True, indent=4)


# Add username to bridge whitelist
def register_device(hue_ip, username):
    url = 'http://%s/api/' % hue_ip
    data = {
        'devicetype': 'ScreenBloom',
        'username': username
    }

    body = json.dumps(data)

    r = requests.post(url, data=body)
    return r.json()


# Return properly formatted list of current Hue light IDs
def get_lights_list(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})

    resource = {
        'which': 'all'
    }

    lights = bridge.light.get(resource)
    lights = lights['resource']
    number_of_lights = len(lights)

    lights_list = []
    for x in range(1, number_of_lights + 1):
        lights_list.append(str(x))

    return ','.join(lights_list)


# Return more detailed information about specified lights
def get_lights_data(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    config_list = config_to_list()
    bulbs = ''.join(config_list[8]).split(',')
    bulbs = [int(i) for i in bulbs]
    selected_bulbs = ''.join(config_list[2]).split(',')
    selected_bulbs = [int(i) for i in selected_bulbs]

    lights = []
    counter = 0
    for bulb in bulbs:
        resource = {
            'which': bulb
        }

        result = bridge.light.get(resource)
        state = result['resource']['state']['on']
        light_name = result['resource']['name']
        light_data = [bulb, state, light_name, int(selected_bulbs[counter])]
        lights.append(light_data)
        counter += 1

    return lights


def create_config(hue_ip, username):
    current_path = os.path.dirname(os.path.abspath(__file__))
    username = username
    bulbs = get_lights_list(hue_ip, username)
    sat = '230'
    bri = '254'
    trans = '15'

    with open('%s/config.txt' % current_path, 'a+') as config_file:
        config_file.write(hue_ip + '\n')
        config_file.write(username + '\n')
        config_file.write(bulbs + '\n')
        config_file.write(sat + '\n')
        config_file.write(bri + '\n')
        config_file.write(trans + '\n')
        config_file.write('False' + '\n')
        config_file.write('False' + '\n')
        config_file.write(bulbs + '\n')

    return None


# Return properly formatted list from config.txt
def config_to_list():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open('%s/config.txt' % current_path, 'r') as config_file:
        config = '\n'.join(config_file).split()

    return config


# Rewrite config file with given arguments
def write_config(selected_bulbs, sat, bri, trans, running, user_exit):
    current_path = os.path.dirname(os.path.abspath(__file__))
    config = config_to_list()

    all_bulbs = config_to_list()[8]
    selected_bulbs = [int(i) for i in selected_bulbs.split(',')]
    all_bulbs = [int(i) for i in all_bulbs.split(',')]

    # Check selected bulbs vs all known bulbs
    bulb_list = []
    counter = 0
    for bulb in all_bulbs:
        if selected_bulbs[counter]:
            bulb_list.append('1')
        else:
            bulb_list.append('0')
        counter += 1

    with open('%s/config.txt' % current_path, 'w+') as config_file:
        config_file.write(config[0] + '\n')
        config_file.write(config[1] + '\n')
        config_file.write(','.join(bulb_list) + '\n')
        config_file.write(sat + '\n')
        config_file.write(bri + '\n')
        config_file.write(trans + '\n')
        config_file.write(running + '\n')
        config_file.write(user_exit + '\n')
        config_file.write(config[8])


# Grab attributes for screen instance
def initialize():
    config = config_to_list()

    ip = config[0]
    devicename = config[1]
    sat = int(config[3])
    bri = int(config[4])
    transition = int(config[5])
    bridge = Bridge(device={'ip': ip}, user={'name': devicename})

    selected_bulbs = [int(i) for i in config_to_list()[2].split(',')]
    all_bulbs = [int(i) for i in config_to_list()[8].split(',')]

    # Check selected bulbs vs all known bulbs
    bulb_list = []
    counter = 0
    for bulb in all_bulbs:
        if selected_bulbs[counter]:
            bulb_list.append(bulb)
        counter += 1

    attributes = ('#FFFFFF', bridge, ip, devicename, bulb_list, sat, bri, transition)

    return attributes


# Get updated attributes, re-initialize screen object
def re_initialize():
    # Attributes
    at = initialize()

    global screen
    screen = Screen(at[0], at[1], at[2], at[3], at[4], at[5], at[6], at[7])


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(dark_pixel_ratio):
    brightness = screen.bri
    min_brightness = 150

    if dark_pixel_ratio >= 95.0:
        brightness -= (dark_pixel_ratio * brightness) / 100
        if brightness < min_brightness:
            brightness = min_brightness

    return int(brightness)


# Updates Hue bulb to specified CIE value
def update_bulb(screen_obj, cie_color, hex_color, dark_ratio):
    brightness = get_brightness(dark_ratio)

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
                        # 'bri': screen_obj.bri,
                        'bri': brightness,
                        'transitiontime': screen_obj.transition
                    }
                }
            }

            screen.bridge.light.update(resource)


# Set bulbs to a standard white color
def update_bulb_default():
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


# Convert an (R, G, B) tuple to #RRGGBB
def tup_to_hex(rgb_tuple):
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


# Grabs screenshot of current window, returns avg color values of all pixels
def screen_avg():
    # Grab image of current screen
    img = ImageGrab.grab()

    # Resize image so it's faster to process
    size = (16, 16)
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
            if pixels[x][0] < 50 and pixels[x][1] < 50 and pixels[x][2] < 50:
                black_pixels += 1
                total_pixels += 1
                continue
            # Ignore transparent pixels
            elif pixels[x][3] > 200 / 255:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
                total_pixels += 1
        # In case pixel doesn't have an alpha channel
        except IndexError:
            # Ignore black pixels
            if pixels[x][0] < 50 and pixels[x][1] < 50 and pixels[x][2] < 50:
                black_pixels += 1
                total_pixels += 1
                continue
            else:
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


# Take 3 snapshots of the screen, average their colors
def screen_avg_avg():
    # start = datetime.now()
    colors = []
    dark_ratio = []
    counter = 0
    for x in range(3):
        results = screen_avg()
        colors.append(results['screen_color'])
        dark_ratio.append(results['dark_ratio'])
        counter += 1

    r = 0
    g = 0
    b = 0

    for entry in colors:
        r += entry[0]
        g += entry[1]
        b += entry[2]

    r_avg = r / len(colors)
    g_avg = g / len(colors)
    b_avg = b / len(colors)

    final_color = (r_avg, g_avg, b_avg)
    hue_color = converter.rgbToCIE1931(final_color[0], final_color[1], final_color[2])
    final_dark_ratio = sum(dark_ratio) / len(dark_ratio)

    data = {
        'hue_color': hue_color,
        'screen_hex': tup_to_hex(final_color),
        'dark_ratio': final_dark_ratio
    }

    # end = datetime.now()
    # time_took = start - end
    # print 'Function took %s microseconds' % str(time_took.microseconds)

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

converter = Converter()  # Class for easy conversion of RGB to Hue CIE