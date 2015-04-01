from PIL import ImageGrab
from beautifulhue.api import Bridge
from time import strftime, sleep
import random
import sys
import traceback
import rgb_cie
import ConfigParser
import requests
import threading
import urllib2
import webbrowser
import os
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
            config_exists = os.path.isfile('config.cfg')
            if config_exists:
                config = ConfigParser.RawConfigParser()
                config.read('config.cfg')
                print 'Config already exists'

                # Wait for 200 status code from server then load up interface
                while not check_server(self.host):
                    sleep(0.2)
                # If the 'user_exit' value is 0, app previously ended without being recorded
                # So we will set the 'running' value to 0
                user_exit = config.get('App State', 'user_exit')
                if user_exit == '0':
                    write_config('App State', 'running', '0')

                # Grab attributes from config file
                atr = initialize()

                # Initialize screen object
                global _screen
                _screen = Screen(*atr)

                url = 'http://%s:5000/' % self.host
                webbrowser.open(url)
            else:
                # Config file doesn't exist, open New User interface
                print 'Config does not exist yet!'
                url = 'http://%s:5000/new-user' % self.host
                webbrowser.open(url)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StartupThread, self).join(timeout)


# Class for running ScreenBloom thread
class ScreenBloomThread(threading.Thread):
    def __init__(self, update):
        super(ScreenBloomThread, self).__init__()
        self.stoprequest = threading.Event()
        self.update = update

    def run(self):
        while not self.stoprequest.isSet():
            run()
            sleep(float(self.update) / 10)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloomThread, self).join(timeout)


# Class for Screen object to hold values during runtime
class Screen(object):
    def __init__(self, bridge, ip, devicename, bulbs, default, rgb, update, bri, min_bri, dynamic_bri):
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.default = default
        self.rgb = rgb
        self.update = update
        self.bri = bri
        self.min_bri = min_bri
        self.dynamic_bri = dynamic_bri

converter = rgb_cie.Converter()  # Class for easy conversion of RGB to Hue CIE


# Write traceback to logfile
def write_traceback():
    with open('log.txt', 'a+') as f:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=f)


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


# Add username to bridge whitelist
def register_device(hue_ip, username):
    url = 'http://%s/api/' % hue_ip
    data = {
        'devicetype': 'ScreenBloom',
        'username': username
    }

    body = json.dumps(data)

    r = requests.post(url, data=body, timeout=5)
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
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    all_lights = config.get('Light Settings', 'all_lights')
    all_lights = [int(i) for i in all_lights.split(',')]
    active_bulbs = config.get('Light Settings', 'active')
    active_bulbs = [int(i) for i in active_bulbs.split(',')]

    lights = []

    for counter, light in enumerate(all_lights):
        resource = {
            'which': light
        }

        result = bridge.light.get(resource)
        state = result['resource']['state']['on']
        light_name = result['resource']['name']
        light_data = [light, state, light_name, int(active_bulbs[counter])]
        lights.append(light_data)

    return lights


# Create config file on first run
def create_config(hue_ip, username):
    config = ConfigParser.RawConfigParser()

    config.add_section('Configuration')
    config.set('Configuration', 'hue_ip', hue_ip)
    config.set('Configuration', 'username', username)
    config.add_section('Light Settings')
    config.set('Light Settings', 'all_lights', get_lights_list(hue_ip, username))
    config.set('Light Settings', 'active', get_lights_list(hue_ip, username))
    config.set('Light Settings', 'update', '12')
    config.set('Light Settings', 'bri', '254')
    config.set('Light Settings', 'default', '200,200,200')
    config.add_section('Dynamic Brightness')
    config.set('Dynamic Brightness', 'running', '0')
    config.set('Dynamic Brightness', 'min_bri', '125')
    config.add_section('Party Mode')
    config.set('Party Mode', 'running', '0')
    config.add_section('App State')
    config.set('App State', 'running', '0')
    config.set('App State', 'user_exit', '0')

    with open('config.cfg', 'wb') as config_file:
        config.write(config_file)

    # Grab attributes from config file
    atr = initialize()

    # Initialize screen object
    global _screen
    _screen = Screen(*atr)


# Rewrite config file with given arguments
def write_config(section, item, value):
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    config.set(section, item, value)

    with open('config.cfg', 'wb') as config_file:
        config.write(config_file)


# Grab attributes for screen instance
def initialize():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    bri = config.get('Light Settings', 'bri')
    bridge = Bridge(device={'ip': ip}, user={'name': username})

    active_lights = config.get('Light Settings', 'active')
    active_lights = [int(i) for i in active_lights.split(',')]
    all_lights = config.get('Light Settings', 'all_lights')
    all_lights = [int(i) for i in all_lights.split(',')]

    dynamic_bri = config.getboolean('Dynamic Brightness', 'running')
    min_bri = config.get('Dynamic Brightness', 'min_bri')

    update = config.get('Light Settings', 'update')
    default = config.get('Light Settings', 'default')
    default = default.split(',')
    default = (int(default[0]), int(default[1]), int(default[2]))

    # Check selected bulbs vs all known bulbs
    bulb_list = []
    for counter, bulb in enumerate(all_lights):
        if active_lights[counter]:
            bulb_list.append(bulb)
        else:
            bulb_list.append(0)

    attributes = (bridge, ip, username, bulb_list, default, default, update, bri, min_bri, dynamic_bri)

    return attributes


# Get updated attributes, re-initialize screen object
def re_initialize():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    # Attributes
    at = initialize()

    global _screen
    _screen = Screen(*at)

    # Update bulbs with new settings
    results = screen_avg()
    default = config.get('Light Settings', 'default').split(',')
    results['rgb'] = (int(default[0]), int(default[1]), int(default[2]))

    try:
        # Update Hue bulbs to avg color of screen
        check_color(_screen, results['rgb'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass


def check_color(screen_obj, new_rgb, dark_ratio):
    wait_time = 0.02

    if screen_obj.dynamic_bri:
        brightness = get_brightness(screen_obj, dark_ratio)
    else:
        brightness = int(screen_obj.bri)

    # Check if bulbs need to be updated
    if screen_obj.rgb == new_rgb:
        # Both color and brightness are same, no update
        if screen_obj.bri == brightness:
            sleep(wait_time)
        # Color is the same but brightness is different, update the bulbs
        else:
            update_bulb(screen_obj, new_rgb, brightness)
    else:
        # Only update brightness if color has bottomed out
        if str(new_rgb) == '(20, 20, 20)':
            print 'Bottomed out, keeping previous color'
            update_bulb(screen_obj, new_rgb, brightness)
        # New color, update bulbs
        else:
            screen_obj.rgb = new_rgb
            update_bulb(screen_obj, new_rgb, brightness)


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(screen_obj, dark_pixel_ratio):
    max_brightness = int(screen_obj.bri)
    min_brightness = int(screen_obj.min_bri)

    normal_range = max_brightness - 1
    new_range = max_brightness - min_brightness

    brightness = max_brightness - (dark_pixel_ratio * max_brightness) / 100
    scaled_brightness = (((brightness - 1) * new_range) / normal_range) + float(screen_obj.min_bri) + 1

    return int(scaled_brightness)


# Updates Hue bulbs to specified CIE value
def update_bulb(screen_obj, new_rgb, bri):
    now = strftime('%I:%M:%S %p')
    print '\nCurrent Color: %s | New Color: %s | Brightness: %d' % (str(screen_obj.rgb), new_rgb, bri)
    print '%s - Updating' % now
    bulbs = screen_obj.bulbs
    hue_color = converter.rgbToCIE1931(screen_obj.rgb[0], screen_obj.rgb[1], screen_obj.rgb[2])
    for bulb in bulbs:
            resource = {
                'which': bulb,
                'data': {
                    'state': {
                        'xy': hue_color,
                        'bri': bri,
                        'transitiontime': int(screen_obj.update)
                    }
                }
            }

            screen_obj.bridge.light.update(resource)


# Set bulbs to a standard white color
def update_bulb_default():
    global _screen
    bulbs = _screen.bulbs
    hue_color = converter.rgbToCIE1931(_screen.default[0], _screen.default[1], _screen.default[2])

    print '\nSetting bulbs to default'
    print 'Current Color: %s | Brightness: %s' % (str(_screen.default), _screen.bri)

    for bulb in bulbs:
            resource = {
                'which': bulb,
                'data': {
                    'state': {
                        'xy': hue_color,
                        'bri': _screen.bri,
                        'transitiontime': int(_screen.update)
                    }
                }
            }

            _screen.bridge.light.update(resource)


# Generate truly random RGB
def party_rgb():
    r = lambda: random.randint(0, 255)
    rgb = (r(), r(), r())
    return rgb


def update_bulb_party():
    global _screen
    bulbs = _screen.bulbs

    print '\nParty Mode! | Brightness: %s' % _screen.bri

    for bulb in bulbs:
            rgb = party_rgb()
            resource = {
                'which': bulb,
                'data': {
                    'state': {
                        'xy': converter.rgbToCIE1931(rgb[0], rgb[1], rgb[2]),
                        'bri': _screen.bri,
                        'transitiontime': int(_screen.update)
                    }
                }
            }

            _screen.bridge.light.update(resource)


def lights_on_off(state):
    global _screen
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    all_lights = [int(i) for i in config.get('Light Settings', 'all_lights').split(',')]
    active_lights = [int(i) for i in config.get('Light Settings', 'active').split(',')]
    selected_lights = []

    for index, light in enumerate(all_lights):
        if active_lights[index] == 1:
            selected_lights.append(light)

    print '\nTurning Selected Lights %s' % state

    if state == 'On':
        state = 'true'
    else:
        state = 'false'

    for light in selected_lights:
        resource = {
            'which': light,
            'data': {
                'state': {
                    'on': state,
                    'transitiontime': int(_screen.update)
                }
            }
        }

        _screen.bridge.light.update(resource)


# Grabs screenshot of current window, returns avg color values of all pixels
def screen_avg():
    # Grab image of current screen
    img = ImageGrab.grab()

    # Resize image so it's faster to process
    size = (16, 16)
    img = img.resize(size)

    # Create list of pixels
    pixels = list(img.getdata())

    threshold = 20
    dark_pixels = 1
    total_pixels = 1
    r = 1
    g = 1
    b = 1

    for red, green, blue in pixels:
        # Don't count pixels that are too dark
        if red < threshold and green < threshold and blue < threshold:
            dark_pixels += 1
            total_pixels += 1
        else:
            r += red
            g += green
            b += blue
            total_pixels += 1

    n = len(pixels)

    r_avg = r / n
    g_avg = g / n
    b_avg = b / n

    # If computed average below darkness threshold, set to the threshold
    rgb = [r_avg, g_avg, b_avg]
    for index, item in enumerate(rgb):
        if item <= threshold:
            rgb[index] = threshold

    rgb = (rgb[0], rgb[1], rgb[2])
    dark_ratio = (float(dark_pixels) / float(total_pixels)) * 100

    data = {
        'rgb': rgb,
        'dark_ratio': dark_ratio
    }

    return data


def run():
    global _screen
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    party_mode_state = config.getboolean('Party Mode', 'running')
    if party_mode_state:
        update_bulb_party()
    else:
        results = screen_avg()

        try:
            check_color(_screen, results['rgb'], results['dark_ratio'])
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass