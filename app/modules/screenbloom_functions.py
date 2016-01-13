from PIL import ImageGrab
from beautifulhue.api import Bridge
from time import strftime, sleep
from flask import redirect, url_for
import random
import sys
import traceback
import rgb_cie
import ConfigParser
import requests
import requests.packages.urllib3
import requests.exceptions
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
    def __init__(self, bridge, ip, devicename, bulbs, default, rgb, update, bri, min_bri):
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.default = default
        self.rgb = rgb
        self.update = update
        self.bri = bri
        self.min_bri = min_bri

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
    config.set('Light Settings', 'default', '200,200,200')
    config.set('Light Settings', 'bri', '254')
    config.set('Light Settings', 'min_bri', '125')
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
    min_bri = config.get('Light Settings', 'min_bri')
    bridge = Bridge(device={'ip': ip}, user={'name': username})

    active_lights = config.get('Light Settings', 'active')
    active_lights = [int(i) for i in active_lights.split(',')]
    all_lights = config.get('Light Settings', 'all_lights')
    all_lights = [int(i) for i in all_lights.split(',')]

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

    attributes = (bridge, ip, username, bulb_list, default, default, update, bri, min_bri)

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
        update_bulbs(_screen, results['rgb'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(screen_obj, dark_pixel_ratio):
    max_brightness = int(screen_obj.bri)
    min_brightness = int(screen_obj.min_bri)

    normal_range = max(1, max_brightness - 1)
    new_range = max_brightness - min_brightness

    brightness = max_brightness - (dark_pixel_ratio * max_brightness) / 100
    scaled_brightness = (((brightness - 1) * new_range) / normal_range) + float(screen_obj.min_bri) + 1

    return int(scaled_brightness)


# Updates Hue bulbs to specified CIE value
def update_bulbs(screen_obj, new_rgb, dark_ratio):
    brightness = get_brightness(screen_obj, dark_ratio)
    hue_color = converter.rgbToCIE1931(new_rgb[0], new_rgb[1], new_rgb[2])
    now = strftime('%I:%M:%S %p')

    print '\nCurrent Color: %s | New Color: %s | Brightness: %d' % (str(screen_obj.rgb), new_rgb, brightness)
    print '%s - Updating' % now

    screen_obj.rgb = new_rgb
    bulbs = screen_obj.bulbs

    for bulb in bulbs:
        resource = {
            'which': bulb,
            'data': {
                'state': {
                    'xy': hue_color,
                    'bri': brightness,
                    'transitiontime': int(screen_obj.update)
                }
            }
        }

        screen_obj.bridge.light.update(resource)


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
            update_bulbs(_screen, results['rgb'], results['dark_ratio'])
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass


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
                        'bri': int(_screen.bri),
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
                        'bri': int(_screen.bri),
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
        state = True
    else:
        state = False

    for light in selected_lights:
        resource = {
            'which': light,
            'data': {
                'state': {
                    'on': state,
                    'bri': int(_screen.bri),
                    'transitiontime': int(_screen.update)
                }
            }
        }

        _screen.bridge.light.update(resource)


# View Logic #############################################################
def get_index_data():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    write_config('App State', 'user_exit', '0')

    hue_ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    update = float(config.get('Light Settings', 'update'))
    if update in (1, 2):
        update = update
    else:
        update = float(update) / 10
    bri = config.get('Light Settings', 'bri')
    min_bri = config.get('Light Settings', 'min_bri')
    default = config.get('Light Settings', 'default')
    default_color = default.split(',')
    lights = get_lights_data(hue_ip, username)

    expanded_lights = ''
    lights_number = len(lights)
    icon_size = 10
    party_mode = config.getboolean('Party Mode', 'running')
    if party_mode:
        party_mode = 1
    else:
        party_mode = 0

    # Splitting up large # of lights to not break interface
    if lights_number > 3:
        temp_lights = list(lights)
        expanded_lights = lights
        lights = temp_lights[0:3]
        icon_size = 4

    data = {
        'update': update,
        'bri': bri,
        'min_bri': min_bri,
        'default': default,
        'default_color': default_color,
        'lights': lights,
        'expanded_lights': expanded_lights,
        'lights_number': lights_number,
        'icon_size': icon_size,
        'username': username,
        'party_mode': party_mode
    }
    return data


def start_screenbloom():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    print 'Firing run function...'

    running = config.get('App State', 'running')
    update = int(config.get('Light Settings', 'update'))

    if running == 'True':
        data = {
            'message': 'ScreenBloom already running'
        }

    else:
        # Rewriting config file with 'Running = True' value
        write_config('App State', 'running', '1')

        global t
        t = ScreenBloomThread(update)
        t.start()

        print 'Hello!'

        data = {
            'message': 'ScreenBloom thread initialized'
        }
    return data


def stop_screenbloom():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    print 'Ending screenBloom thread...'

    # Rewriting config file with 'Running = False' value
    write_config('App State', 'running', '0')
    write_config('App State', 'user_exit', '1')

    # End currently running threads
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not running'

    # Update bulbs to a normal white color
    update_bulb_default()

    data = {
        'message': 'Successfully ended screenBloom thread'
    }
    return data


# Parses arguments from AJAX call and passes them to register_device()
def register_logic(user, ip, host):
    if not ip:
        print 'Hue IP not entered manually'
        # Attempting to grab IP from Philips uPNP app
        try:
            requests.packages.urllib3.disable_warnings()
            url = 'https://www.meethue.com/api/nupnp'
            r = requests.get(url, verify=False).json()
            ip = str(r[0]['internalipaddress'])
        except Exception as e:
            print e
            write_traceback()
            error_type = 'manual'
            error_description = 'Error grabbing Hue IP, redirecting to manual entry...'
            print error_description
            data = {
                'success': False,
                'error_type': error_type,
                'error_description': error_description,
                'host': host
            }
            return data
    try:
        # Send post request to Hue bridge to register new username, return response as JSON
        result = register_device(ip, user)
        print result
        temp_result = result[0]
        result_type = ''
        for k, v in temp_result.items():
            result_type = str(k)
        if result_type == 'error':
            error_type = result[0]['error']['type']
            print error_type
            error_description = result[0]['error']['description']

            data = {
                'success': False,
                'error_type': str(error_type),
                'error_description': str(error_description)
            }
            return data
        else:
            create_config(ip, user)

            data = {
                'success': True,
                'message': 'Success!'
            }
            return data
    except requests.exceptions.ConnectionError:
        print 'Something went wrong with the connection, please try again...'
        data = {
            'success': False,
            'error_type': 'Invalid URL'
        }
        return data
    except IOError:
        print 'Permission denied, administrator rights needed..'
        data = {
            'success': False,
            'error_type': 'permission'
        }
        return data


# Parses args from AJAX and updates config file
def update_config_logic(bri, bulbs, update, default, min_bri, party_mode):
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    settings = [
        ('Light Settings', 'active', bulbs),
        ('Light Settings', 'update', update),
        ('Light Settings', 'default', default),
        ('Light Settings', 'bri', bri),
        ('Light Settings', 'min_bri', min_bri),
        ('Party Mode', 'running', party_mode),
        ('App State', 'running', '0'),
        ('App State', 'user_exit', '0')
    ]

    try:
        if t.isAlive():
            print 'Thread is running!'
            t.join()
            settings[6] = ('App State', 'running', '1')
            for s in settings:
                write_config(s[0], s[1], s[2])
            re_initialize()
            return redirect(url_for('start'))
        else:
            print 'Thread is not running!'
            for s in settings:
                write_config(s[0], s[1], s[2])
            re_initialize()
    except NameError:
        print 't not defined yet!'
        for s in settings:
                write_config(s[0], s[1], s[2])
        re_initialize()

    data = {
        'message': 'Updated config file!'
    }
    return data


# Returns dictionary of current settings for display in front end
def get_settings_logic():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    active_lights = config.get('Light Settings', 'active')
    all_lights = config.get('Light Settings', 'all_lights')

    data = {
        'bulbs-value': [int(i) for i in active_lights.split(',')],
        'running-state': config.get('App State', 'running'),
        'all-bulbs': [int(i) for i in all_lights.split(',')],
        'bri-value': config.get('Light Settings', 'bri'),
        'min-bri': config.get('Light Settings', 'min_bri'),
        'update-value': config.get('Light Settings', 'update'),
        'default': config.get('Light Settings', 'default'),
        'party-mode': config.get('Party Mode', 'running')
    }
    return data