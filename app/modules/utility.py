from vendor.wmi import sampler
from config import params
import hue_interface
import ConfigParser
import icon_names
import traceback
import requests
import StringIO
import logging
import socket
import random
import json
import sys
import os


def dll_check():
    try:
        from desktopmagic.screengrab_win32 import getDisplaysAsImages
    except ImportError as e:
        print e
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
        import sb_controller
        atr = sb_controller.initialize()
        return True
    except ConfigParser.NoOptionError as e:
        print e
        return False
    except ConfigParser.NoSectionError as e:
        print e
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
        print 'Can\'t find display index, switching to default'
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
    color_mode_enabled = config.getboolean('Configuration', 'color_mode_enabled')

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
    black_rgb = config.get('Light Settings', 'black_rgb')
    display_index = config.get('Light Settings', 'display_index')
    color_mode = config.get('Light Settings', 'color_mode')

    system_monitoring_enabled = config.getboolean('System Monitoring', 'enabled')
    system_monitoring_mode = config.get('System Monitoring', 'mode')
    system_monitoring_interval = config.get('System Monitoring', 'interval')

    cpu_warning_temp = config.get('System Monitoring', 'cpu_warning_temp')
    cpu_extreme_temp = config.get('System Monitoring', 'cpu_extreme_temp')
    cpu_warning_color = config.get('System Monitoring', 'cpu_warning_color')
    cpu_extreme_color = config.get('System Monitoring', 'cpu_extreme_color')
    gpu_warning_temp = config.get('System Monitoring', 'gpu_warning_temp')
    gpu_extreme_temp = config.get('System Monitoring', 'gpu_extreme_temp')
    gpu_warning_color = config.get('System Monitoring', 'gpu_warning_color')
    gpu_extreme_color = config.get('System Monitoring', 'gpu_extreme_color')

    party_mode = config.getboolean('Party Mode', 'running')

    return {
        'ip': ip,
        'username': username,
        'autostart': autostart,
        'current_preset': current_preset,
        'color_mode_enabled': color_mode_enabled,
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
        'black_rgb': black_rgb,
        'display_index': display_index,
        'color_mode': color_mode,
        'system_monitoring_enabled': system_monitoring_enabled,
        'system_monitoring_mode': system_monitoring_mode,
        'system_monitoring_interval': system_monitoring_interval,
        'cpu_warning_temp': cpu_warning_temp,
        'cpu_extreme_temp': cpu_extreme_temp,
        'cpu_warning_color': cpu_warning_color,
        'cpu_extreme_color': cpu_extreme_color,
        'gpu_warning_temp': gpu_warning_temp,
        'gpu_extreme_temp': gpu_extreme_temp,
        'gpu_warning_color': gpu_warning_color,
        'gpu_extreme_color': gpu_extreme_color,
        'party_mode': party_mode
    }


def get_json_filepath():
    return os.getenv('APPDATA') + '\\screenBloom_presets.json'


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


def main_loop_readout(screen_object):
    if not screen_object.party_mode:
        parse_method = 'standard' if not screen_object.zone_state else 'zones'
        color_mode = screen_object.color_mode
        color_mode_enabled = 'Parse Method: %s | Color Mode: %s' % (parse_method, color_mode) if screen_object.color_mode_enabled else 'Color Mode: disabled'
        system_monitoring_enabled = ' | Monitoring: '
        system_monitoring_enabled += 'enabled' if screen_object.system_monitoring_enabled else 'disabled'

        readout_string = '\n%s' % color_mode_enabled
        if params.BUILD == 'win':
            readout_string += system_monitoring_enabled

        print readout_string


def get_ohm_interface():
    return sampler.WMISampler(logging.getLogger(), 'Sensor', ['name', 'value'], namespace='root\OpenHardwareMonitor')


# Grab all kinds of good system info from Open Hardware Monitor
def get_system_temps(sensor_sample):
    cpu_temps = {}
    gpu_temps = {}
    count = 1

    sorted_sensor_sample = sorted(sensor_sample, key=lambda k: k['value'], reverse=True)
    for entry in sorted_sensor_sample:
        name = entry['name']
        value = entry['value']

        if value == 0.0:
            continue
        elif value > 1000:
            continue
        elif 'Core' not in name:
            continue
        elif 'GPU' not in name and 'CPU' not in name:
            continue

        # print entry
        if 'CPU Cores' in entry['name']:
            continue
        if 'CPU Core' in entry['name']:
            if not entry['name'] in cpu_temps:  # Grab 2nd CPU Core values
                cpu_temps[entry['name']] = entry['value']
        if 'GPU Core' in entry['name']:
            key = entry['name'] + '_' + str(count)
            gpu_temps[key] = entry['value']
            count += 1

    sorted_gpu_temp = sorted(gpu_temps, key=lambda k: k[1])
    try:
        gpu_temp = gpu_temps[sorted_gpu_temp[1]]
    except IndexError:
        try:
            gpu_temp = gpu_temps[sorted_gpu_temp[0]]
        except IndexError:
            print 'No results, Open Hardware Monitor is probably not running...'
            return {}

    if gpu_temp < 10:
        gpu_temp = None

    temps = {
        'cpu_temps': cpu_temps,
        'gpu_temp': gpu_temp
    }

    return temps
