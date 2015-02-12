from PIL import ImageGrab
from rgb_cie import Converter
from beautifulhue.api import Bridge
import ConfigParser
import requests
import threading
import urllib2
import webbrowser
import os
import time
import json

converter = Converter()  # Class for easy conversion of RGB to Hue CIE


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
                    time.sleep(0.2)
                # If the 'user_exit' value is 0, app previously ended without being recorded
                # So we will set the 'running' value to 0
                user_exit = config.get('App State', 'user_exit')
                if user_exit == '0':
                    write_config('App State', 'running', '0')

                global atr, screen

                # Grab attributes from config file
                atr = initialize()

                # Initialize screen object
                screen = Screen(*atr)

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
    def __init__(self, transition):
        super(ScreenBloomThread, self).__init__()
        self.transition = transition
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.isSet():
            run()
            time.sleep(1)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloomThread, self).join(timeout)


# Class for Screen object to hold values during runtime
class Screen(object):
    def __init__(self, hex_color, bridge, ip, devicename, bulbs, sat, bri, transition, dynamic_bri, min_bri):
        self.hex_color = hex_color
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.sat = sat
        self.bri = bri
        self.transition = transition
        self.dynamic_bri = dynamic_bri
        self.min_bri = min_bri


# Temporary function to help development
def print_hue_config():
    temp_bridge = Bridge(device={'ip': '192.168.0.2'}, user={'name': 'tylerkershner'})
    resource = {'which': 'bridge'}

    result = temp_bridge.config.get(resource)
    print json.dumps(result, sort_keys=True, indent=4)


# Grab Flask secret key from file
def get_key():
    path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.abspath(os.path.join(path, os.pardir))
    file_object = filepath + '/secret_key.txt'

    with open(file_object, 'r') as f:
        data = f.read()
        return data


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
    current_path = os.path.dirname(os.path.abspath(__file__))
    config = ConfigParser.RawConfigParser()

    config.add_section('Configuration')
    config.set('Configuration', 'hue_ip', hue_ip)
    config.set('Configuration', 'username', username)
    config.add_section('Light Settings')
    config.set('Light Settings', 'all_lights', get_lights_list(hue_ip, username))
    config.set('Light Settings', 'active', get_lights_list(hue_ip, username))
    config.set('Light Settings', 'sat', '255')
    config.set('Light Settings', 'bri', '254')
    config.set('Light Settings', 'trans', '15')
    config.add_section('Dynamic Brightness')
    config.set('Dynamic Brightness', 'running', '0')
    config.set('Dynamic Brightness', 'min_bri', '125')
    config.add_section('App State')
    config.set('App State', 'running', '0')
    config.set('App State', 'user_exit', '0')

    with open('%s/config.cfg' % current_path, 'wb') as config_file:
        config.write(config_file)


# Rewrite config file with given arguments
def write_config(section, item, value):
    current_path = os.path.dirname(os.path.abspath(__file__))
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    config.set(section, item, value)

    with open('%s/config.cfg' % current_path, 'wb') as config_file:
        config.write(config_file)


# Grab attributes for screen instance
def initialize():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    sat = config.get('Light Settings', 'sat')
    bri = config.get('Light Settings', 'bri')
    transition = config.get('Light Settings', 'trans')
    bridge = Bridge(device={'ip': ip}, user={'name': username})

    active_lights = config.get('Light Settings', 'active')
    active_lights = [int(i) for i in active_lights.split(',')]
    all_lights = config.get('Light Settings', 'all_lights')
    all_lights = [int(i) for i in all_lights.split(',')]

    dynamic_bri = config.getboolean('Dynamic Brightness', 'running')
    min_bri = config.get('Dynamic Brightness', 'min_bri')

    # Check selected bulbs vs all known bulbs
    bulb_list = []
    for counter, bulb in enumerate(all_lights):
        if active_lights[counter]:
            bulb_list.append(bulb)
        else:
            bulb_list.append(0)

    attributes = ('#FFFFFF', bridge, ip, username, bulb_list, sat, bri, transition, dynamic_bri, min_bri)

    return attributes


# Get updated attributes, re-initialize screen object
def re_initialize():
    # Attributes
    at = initialize()

    global screen
    screen = Screen(*at)

    # Update bulbs with new settings
    results = screen_avg()
    try:
        # Update Hue bulbs to avg color of screen
        update_bulb(screen, results['hue_color'], results['screen_hex'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(dark_pixel_ratio, min_bri):
    brightness = int(screen.bri)
    min_brightness = int(min_bri)

    brightness -= (dark_pixel_ratio * brightness) / 100
    if brightness < min_brightness:
        brightness = min_brightness

    return int(brightness)


# Updates Hue bulb to specified CIE value
def update_bulb(screen_obj, cie_color, hex_color, dark_ratio):
    # If dynamic brightness enabled, grab brightness from function
    if screen_obj.dynamic_bri:
        brightness = get_brightness(dark_ratio, screen_obj.min_bri)
    else:
        brightness = screen_obj.bri

    if hex_color == screen.hex_color:
        print 'Color is the same, no update necessary.'
        time.sleep(0.02)
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


# Grabs screenshot of current window, returns avg color values of all pixels
def screen_avg():
    # Grab image of current screen
    img = ImageGrab.grab()

    # Resize image so it's faster to process
    size = (16, 16)
    img = img.resize(size)

    # Create list of pixels
    pixels = list(img.getdata())

    threshold = 70
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
    screen_color = [r_avg, g_avg, b_avg]
    for index, item in enumerate(screen_color):
        if item <= threshold:
            screen_color[index] = threshold

    screen_color = (screen_color[0], screen_color[1], screen_color[2])
    screen_hex = '#%02x%02x%02x' % screen_color  # Convert an (R, G, B) tuple to #RRGGBB
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    dark_ratio = (float(dark_pixels) / float(total_pixels)) * 100

    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
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