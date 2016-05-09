from PIL import ImageGrab
from beautifulhue.api import Bridge
from time import strftime, sleep
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


app_path = ''
if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
elif __file__:
    app_path = os.path.dirname(__file__)

converter = rgb_cie.Converter()  # Class for easy conversion of RGB to Hue CIE


# Class for the start-up process
class StartupThread(threading.Thread):
    def __init__(self, host):
        super(StartupThread, self).__init__()
        self.stoprequest = threading.Event()
        self.host = host

    def run(self):
        if not self.stoprequest.isSet():
            # Check if config file has been created yet
            config_exists = os.path.isfile(app_path + '/screenbloom_config.cfg')
            if config_exists:
                print 'Config already exists'
                config = ConfigParser.RawConfigParser()
                config.read(app_path + '/screenbloom_config.cfg')
                write_config('App State', 'running', '0')

                # Wait for 200 status code from server then load up interface
                while not check_server(self.host):
                    sleep(0.2)

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
        self.update = float(update)

    def run(self):
        while not self.stoprequest.isSet():
            run()
            sleep(self.update)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloomThread, self).join(timeout)


# Class for Screen object to hold values during runtime
class Screen(object):
    def __init__(self, bridge, ip, devicename, bulbs, default, rgb, update, max_bri, min_bri):
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.default = default
        self.rgb = rgb
        self.update = update
        self.max_bri = max_bri
        self.min_bri = min_bri


# Write traceback to logfile
def write_traceback():
    with open('log.txt', 'a+') as f:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=f)


# Generate truly random RGB
def party_rgb():
    r = lambda: random.randint(0, 255)
    rgb = (r(), r(), r())
    return rgb


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


# Return list of current Hue light IDs
def get_lights_list(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    resource = {
        'which': 'all'
    }
    lights = bridge.light.get(resource)
    lights = lights['resource']

    lights_list = []
    for light in lights:
        lights_list.append(str(light['id']))
    return lights_list


# Return more detailed information about specified lights
def get_lights_data(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')
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

        # Skip unavailable lights
        if type(result['resource']) is dict:
            state = result['resource']['state']['on']
            light_name = result['resource']['name']
            light_data = [light, state, light_name, int(active_bulbs[counter])]
            lights.append(light_data)

    return lights


# Create config file on first run
def create_config(hue_ip, username):
    config = ConfigParser.RawConfigParser()
    lights = get_lights_list(hue_ip, username)
    active = ','.join([str(0) for light in lights])

    config.add_section('Configuration')
    config.set('Configuration', 'hue_ip', hue_ip)
    config.set('Configuration', 'username', username)
    config.add_section('Light Settings')
    config.set('Light Settings', 'all_lights', ','.join(lights))
    config.set('Light Settings', 'active', active)
    config.set('Light Settings', 'update', '1.2')
    config.set('Light Settings', 'default', '255,250,240')
    config.set('Light Settings', 'max_bri', '254')
    config.set('Light Settings', 'min_bri', '125')
    config.add_section('Party Mode')
    config.set('Party Mode', 'running', '0')
    config.add_section('App State')
    config.set('App State', 'running', '0')

    with open(app_path + '/screenbloom_config.cfg', 'wb') as config_file:
        config.write(config_file)

    # Grab attributes from config file
    atr = initialize()

    # Initialize screen object
    global _screen
    _screen = Screen(*atr)


# Rewrite config file with given arguments
def write_config(section, item, value):
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')
    config.set(section, item, value)

    with open(app_path + '/screenbloom_config.cfg', 'wb') as config_file:
        config.write(config_file)


# Grab attributes for screen instance
def initialize():
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')

    ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    max_bri = config.get('Light Settings', 'max_bri')
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
        try:
            if active_lights[counter]:
                bulb_list.append(bulb)
            else:
                bulb_list.append(0)
        except IndexError:
            bulb_list.append(0)

    return bridge, ip, username, bulb_list, default, default, update, max_bri, min_bri


# Get updated attributes, re-initialize screen object
def re_initialize():
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')

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
        update_bulbs(results['rgb'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(screen_obj, dark_pixel_ratio):
    max_brightness = int(screen_obj.max_bri)
    min_brightness = int(screen_obj.min_bri)

    normal_range = max(1, max_brightness - 1)
    new_range = max_brightness - min_brightness

    brightness = max_brightness - (dark_pixel_ratio * max_brightness) / 100
    scaled_brightness = (((brightness - 1) * new_range) / normal_range) + float(screen_obj.min_bri) + 1

    return int(scaled_brightness)


# Updates Hue bulbs to specified RGB value
def update_bulbs(new_rgb, dark_ratio):
    brightness = get_brightness(_screen, dark_ratio)

    now = strftime('%I:%M:%S %p')
    print '\nCurrent Color: %s | New Color: %s | Brightness: %d' % (str(_screen.rgb), new_rgb, brightness)
    print '%s - Updating' % now

    send_light_commands(new_rgb, brightness)
    _screen.rgb = new_rgb


# Set bulbs to specified default color
def update_bulb_default():
    print '\nSetting bulbs to default'
    print 'Current Color: %s | Brightness: %s' % (str(_screen.default), _screen.max_bri)

    default_rgb = _screen.default[0], _screen.default[1], _screen.default[2]
    send_light_commands(default_rgb, _screen.max_bri)


def update_bulb_party():
    print '\nParty Mode! | Brightness: %d' % int(_screen.max_bri)
    send_light_commands(party_rgb(), _screen.max_bri)


def get_transition_time(update_speed):
    update_speed = int(float(update_speed) * 10)
    return update_speed if update_speed > 3 else 3


def send_light_commands(rgb, bri):
    bulbs = _screen.bulbs
    hue_color = converter.rgbToCIE1931(rgb[0], rgb[1], rgb[2])
    for bulb in bulbs:
        resource = {
            'which': bulb,
            'data': {
                'state': {
                    'xy': hue_color,
                    'bri': int(bri),
                    'transitiontime': get_transition_time(_screen.update)
                }
            }
        }
        _screen.bridge.light.update(resource)


def lights_on_off(state):
    print '\nTurning Selected Lights %s' % state

    active_lights = _screen.bulbs
    state = True if state == 'On' else False

    for light in active_lights:
        resource = {
            'which': light,
            'data': {
                'state': {
                    'on': state,
                    'bri': int(_screen.max_bri),
                    'transitiontime': _screen.update
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

    threshold = 10
    dark_pixels = 1
    total_pixels = 1
    r = 1
    g = 1
    b = 1

    for red, green, blue, alpha in pixels:
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
    rgb = [r_avg, g_avg, b_avg]

    # If computed average below darkness threshold, set to the threshold
    for index, item in enumerate(rgb):
        if item <= threshold:
            rgb[index] = threshold

    data = {
        'rgb': (rgb[0], rgb[1], rgb[2]),
        'dark_ratio': float(dark_pixels) / float(total_pixels) * 100
    }
    return data


def run():
    global _screen
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')
    party_mode_state = config.getboolean('Party Mode', 'running')
    if party_mode_state:
        update_bulb_party()
    else:
        results = screen_avg()
        try:
            update_bulbs(results['rgb'], results['dark_ratio'])
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass


# View Logic #############################################################
def get_index_data():
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')

    state = config.get('App State', 'running')
    hue_ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    update = config.get('Light Settings', 'update')
    max_bri = config.get('Light Settings', 'max_bri')
    min_bri = config.get('Light Settings', 'min_bri')
    default = config.get('Light Settings', 'default')
    default_color = default.split(',')
    lights = get_lights_data(hue_ip, username)
    party_mode = config.getboolean('Party Mode', 'running')

    icon_size = 10
    if len(lights) > 3:
        icon_size = 4

    data = {
        'state': state,
        'update': update,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'default': default,
        'default_color': default_color,
        'lights': lights,
        'lights_number': len(lights),
        'icon_size': icon_size,
        'username': username,
        'party_mode': party_mode
    }
    return data


def start_screenbloom():
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')
    state = int(config.get('App State', 'running'))
    update = config.get('Light Settings', 'update')

    if update:
        state = False

    if state:
        data = {
            'message': 'ScreenBloom already running'
        }
    else:
        write_config('App State', 'running', '1')

        global t
        t = ScreenBloomThread(update)
        t.start()

        print '\nHello!'

        data = {
            'message': 'ScreenBloom thread initialized'
        }
    return data


def stop_screenbloom():
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')

    print '\nEnding screenBloom thread...'

    write_config('App State', 'running', '0')

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


def restart_check():
    global t
    config = ConfigParser.RawConfigParser()
    config.read(app_path + '/screenbloom_config.cfg')
    update = config.get('Light Settings', 'update')

    try:
        if t.isAlive():
            print 'Restarting thread...'
            t.join()
            re_initialize()
            write_config('App State', 'running', '1')

            t = ScreenBloomThread(update)
            t.start()

            print '\nHello!'
        else:
            re_initialize()
    except NameError:
        print 'Thread does not exist yet'
        re_initialize()


# Registration ######################################################
# Parses arguments from AJAX call and passes them to register_device()
def register_logic(ip, host):
    if not ip:
        print 'Hue IP not entered manually'
        # Attempting to grab IP from Philips uPNP app
        try:
            print 'Attempting to grab bridge IP...'
            requests.packages.urllib3.disable_warnings()
            url = 'https://www.meethue.com/api/nupnp'
            r = requests.get(url, verify=False).json()
            ip = str(r[0]['internalipaddress'])
            print 'Success!  Hue IP: %s' % ip
        except Exception as e:
            write_traceback()
            error_type = 'manual'
            error_description = 'Error grabbing Hue IP, redirecting to manual entry...'
            data = {
                'success': False,
                'error_type': error_type,
                'error_description': error_description,
                'host': host
            }
            return data
    try:
        print 'Attempting to register app with Hue bridge...'
        # Send post request to Hue bridge to register new username, return response as JSON
        result = register_device(ip)
        temp_result = result[0]
        result_type = ''
        for k, v in temp_result.items():
            result_type = str(k)
        if result_type == 'error':
            error_type = result[0]['error']['type']
            error_description = result[0]['error']['description']
            data = {
                'success': False,
                'error_type': str(error_type),
                'error_description': str(error_description)
            }
            return data
        else:
            username = temp_result[result_type]['username']
            create_config(ip, username)
            data = {
                'success': True,
                'message': 'Success!'
            }
            return data
    except requests.exceptions.ConnectionError:
        data = {
            'success': False,
            'error_type': 'Invalid URL',
            'error_description': 'Something went wrong with the connection, please try again...'
        }
        return data
    except IOError:
        data = {
            'success': False,
            'error_type': 'permission',
            'error_description': 'Permission denied, administrator rights needed..'
        }
        return data


# Add username to bridge whitelist
def register_device(hue_ip):
    url = 'http://%s/api/' % hue_ip
    data = {
        'devicetype': 'ScreenBloom'
    }
    body = json.dumps(data)
    r = requests.post(url, data=body, timeout=5)
    return r.json()
