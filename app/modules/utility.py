from config import params
import hue_interface
import ConfigParser
import icon_names
import traceback
import requests
import StringIO
import socket
import random
import json
import sys
import os


def dll_check():
    try:
        from desktopmagic.screengrab_win32 import getDisplaysAsImages
    except ImportError as e:
        # print e
        return False
    return True

if dll_check():
    import img_proc

if params.ENV == 'prod':
    current_path = ''
elif params.ENV == 'dev':
    current_path = os.path.dirname(os.path.abspath(__file__)) + '\\'


# Ping Google's DNS server to reveal IP
def get_local_host():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    local_host = (s.getsockname()[0])
    s.close()
    return local_host


def config_check():
    try:
        # Grab config variables, will throw an error if there is a mismatch
        test = get_config_dict()
        return True
    except ConfigParser.NoOptionError as e:
        # print e
        return False
    except ConfigParser.NoSectionError as e:
        # print e
        return False


def get_config_path():
    config_path = ''

    if params.BUILD == 'win':
        config_path = os.getenv('APPDATA')
    elif params.BUILD == 'mac':
        config_path = ''
        if getattr(sys, 'frozen', False):
            config_path = os.path.dirname(sys.executable)
        elif __file__:
            config_path = os.path.dirname(__file__)

    return config_path + '\\screenBloom_config.cfg'


# Check server status
def check_server(host, port):
    try:
        r = requests.get('http://%s:%d/new-user' % (host, port))
        response = r.status_code
    except requests.ConnectionError:
        response = 404
    if response == 200:
        return True
    else:
        return False


# Rewrite config file with given arguments
def write_config(section, item, value):
    config = ConfigParser.RawConfigParser()
    config.read(get_config_path())
    config.set(section, item, value)

    with open(get_config_path(), 'wb') as config_file:
        config.write(config_file)


# Write traceback to logfile
def write_traceback():
    with open('log.txt', 'a+') as f:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=f)


# Generate random RGB
def party_rgb():
    r = lambda: random.randint(0, 255)
    rgb = (r(), r(), r())
    return rgb


def get_screenshot(display_index):
    # Win version
    if params.BUILD == 'win':
        from desktopmagic.screengrab_win32 import getDisplaysAsImages
        imgs = getDisplaysAsImages()
        try:
            img = imgs[int(display_index)]
        except IndexError:
            img = imgs[0]
    # Mac version
    else:
        from PIL import ImageGrab
        img = ImageGrab.grab()

    tmp = StringIO.StringIO()
    img.save(tmp, format="PNG")
    b64_data = tmp.getvalue().encode('base64')
    return b64_data


def get_multi_monitor_screenshots():
    imgs = img_proc.get_monitor_screenshots()
    screenshots = []

    for img in imgs:
        tmp = StringIO.StringIO()
        img.save(tmp, format="PNG")
        b64_data = tmp.getvalue().encode('base64')
        screenshots.append(b64_data)

    return screenshots


def display_check(_screen):
    displays = img_proc.get_monitor_screenshots()
    try:
        displays[int(_screen.display_index)]
    except IndexError as e:
        # print 'Can\'t find display index, switching to default'
        write_config('Light Settings', 'display_index', 0)
        _screen.display_index = 0
    return


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(_screen, max_bri, min_bri, dark_pixel_ratio):
    max_bri = int(max_bri)
    min_bri = int(min_bri)

    normal_range = max(1, max_bri - 1)
    new_range = max_bri - min_bri

    brightness = max_bri - (dark_pixel_ratio * max_bri) / 100
    scaled_brightness = (((brightness - 1) * new_range) / normal_range) + float(min_bri) + 1

    # Global brightness check
    if int(scaled_brightness) < int(_screen.min_bri):
        scaled_brightness = int(_screen.min_bri)
    elif int(scaled_brightness) > int(_screen.max_bri):
        scaled_brightness = int(_screen.max_bri)

    return int(scaled_brightness)


# Convert update speed to ms, check lower bound
def get_transition_time(update_speed):
    update_speed = int(float(update_speed) * 10)
    return update_speed if update_speed > 2 else 2


def get_config_dict():
    config = ConfigParser.RawConfigParser()
    config.read(get_config_path())

    ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    autostart = config.getboolean('Configuration', 'auto_start')
    current_preset = config.get('Configuration', 'current_preset')

    all_lights = config.get('Light Settings', 'all_lights')
    active = config.get('Light Settings', 'active')
    bulb_settings = config.get('Light Settings', 'bulb_settings')
    update = config.get('Light Settings', 'update')
    update_buffer = config.get('Light Settings', 'update_buffer')
    default = config.get('Light Settings', 'default')
    max_bri = config.get('Light Settings', 'max_bri')
    min_bri = config.get('Light Settings', 'min_bri')
    zones = config.get('Light Settings', 'zones')
    zone_state = config.getboolean('Light Settings', 'zone_state')
    display_index = config.get('Light Settings', 'display_index')
    sat = config.get('Light Settings', 'sat')

    party_mode = config.getboolean('Party Mode', 'running')

    app_state = config.getboolean('App State', 'running')

    return {
        'ip': ip,
        'username': username,
        'autostart': autostart,
        'current_preset': current_preset,
        'all_lights': all_lights,
        'active': active,
        'bulb_settings': bulb_settings,
        'update': update,
        'update_buffer': update_buffer,
        'default': default,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'zones': zones,
        'zone_state': zone_state,
        'display_index': display_index,
        'sat': sat,
        'party_mode': party_mode,
        'app_state': app_state
    }


def get_json_filepath():
    return os.getenv('APPDATA') + '\\screenBloom_presets.json'


def get_all_presets():
    filepath = get_json_filepath()
    presets = []
    if os.path.isfile(filepath):
        with open(filepath) as data_file:
            presets = json.load(data_file)
    return presets


def get_preset_by_number(preset_number):
    with open(get_json_filepath()) as data_file:
        presets = json.load(data_file)
        key = 'preset_' + str(preset_number)
        return presets[key]


# Quickly get Python list of ~500 Font Awesome icon names
def get_fa_class_names():
    return icon_names.preset_icon_names


# Will continue to expand this function as the bulb_settings JSON gets added to
def get_current_light_settings():
    config_dict = get_config_dict()
    lights_data = hue_interface.get_lights_data(config_dict['ip'], config_dict['username'])
    light_settings = {}
    for light in lights_data:
        light_settings[str(light[0])] = {
            'name': light[2],
            'model_id': light[4],
            'gamut': hue_interface.get_gamut(light[4])
        }
    return light_settings


def get_hue_initial_state(ip, username):
    light_data = hue_interface.get_lights_data(ip, username)

    initial_lights_state = {}
    for light in light_data:
        initial_lights_state[light[0]] = {
            'state': light[1],
            'bri': light[5],
            'xy': light[6]
        }
    return initial_lights_state
