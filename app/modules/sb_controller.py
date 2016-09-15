from beautifulhue.api import Bridge
from time import sleep
import hue_interface
import ConfigParser
import threading
import img_proc
import urllib2
import utility
import random
import json
import ast
import os


# Class for running ScreenBloom thread
class ScreenBloom(threading.Thread):
    def __init__(self, update):
        super(ScreenBloom, self).__init__()
        self.stoprequest = threading.Event()
        self.update = float(update)

    def run(self):
        while not self.stoprequest.isSet():
            run()
            sleep(.01)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloom, self).join(timeout)


# Class for Screen object to hold values during runtime
class Screen(object):
    def __init__(self, bridge, ip, devicename, bulbs, default, rgb, update,
                 update_buffer, max_bri, min_bri, zones, zone_state, mode,
                 black_rgb, display_index):
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.default = default
        self.rgb = rgb
        self.update = update
        self.update_buffer = update_buffer
        self.max_bri = max_bri
        self.min_bri = min_bri
        self.zones = zones
        self.zone_state = zone_state
        self.mode = mode
        self.black_rgb = black_rgb
        self.display_index = display_index


def start():
    # Grab attributes from config file
    atr = initialize()
    global _screen
    _screen = Screen(*atr)


def get_screen_object():
    global _screen
    return _screen


# Grab attributes for screen instance
def initialize():
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())

    ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    bridge = Bridge(device={'ip': ip}, user={'name': username})

    max_bri = config.get('Light Settings', 'max_bri')
    min_bri = config.get('Light Settings', 'min_bri')

    active_lights = config.get('Light Settings', 'active')
    active_lights = [int(i) for i in active_lights.split(',')]

    all_lights = config.get('Light Settings', 'all_lights')
    all_lights = [int(i) for i in all_lights.split(',')]

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

    update = config.get('Light Settings', 'update')
    update_buffer = config.get('Light Settings', 'update_buffer')

    default = config.get('Light Settings', 'default').split(',')
    default = (int(default[0]), int(default[1]), int(default[2]))

    zones = config.get('Light Settings', 'zones')
    zones = ast.literal_eval(zones)

    zone_state = config.getboolean('Light Settings', 'zone_state')

    mode = 'dominant'
    # mode = 'average'

    black_rgb = config.get('Light Settings', 'black_rgb').split(',')
    black_rgb = (int(black_rgb[0]), int(black_rgb[1]), int(black_rgb[2]))

    display_index = config.get('Light Settings', 'display_index')

    return bridge, ip, username, bulb_list, default, default, \
           update, update_buffer, max_bri, min_bri, zones, zone_state, mode, \
           black_rgb, display_index


# Get updated attributes, re-initialize screen object
def re_initialize():
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())

    # Attributes
    at = initialize()

    global _screen
    _screen = Screen(*at)

    # Update bulbs with new settings
    results = img_proc.screen_avg(_screen)

    try:
        # Update Hue bulbs to avg color of screen
        update_bulbs(results['rgb'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass


# Updates Hue bulbs to specified RGB value
def update_bulbs(new_rgb, dark_ratio):
    global _screen
    brightness = utility.get_brightness(_screen, dark_ratio)
    send_light_commands(new_rgb, brightness)
    _screen.rgb = new_rgb


# Set bulbs to saved default color
def update_bulb_default():
    global _screen
    default_rgb = _screen.default[0], _screen.default[1], _screen.default[2]
    send_light_commands(default_rgb, _screen.max_bri)


# Set bulbs to random RGB
def update_bulb_party():
    global _screen
    print '\nParty Mode! | Brightness: %d' % int(_screen.max_bri)
    party_color = utility.party_rgb()
    send_light_commands(party_color, _screen.max_bri, party=True)


# Used by standard mode
def send_light_commands(rgb, bri, party=False):
    global _screen
    for bulb in _screen.bulbs:
        if party:
            rgb = utility.party_rgb()
            try:
                bri = random.randrange(int(_screen.min_bri), int(bri) + 1)
            except ValueError as e:
                print e
                continue
        hue_interface.send_rgb_to_bulb(bulb, rgb, bri)


# Main loop
def run():
    sleep(float(_screen.update_buffer))

    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    party_mode = config.getboolean('Party Mode', 'running')
    zone_mode = config.getboolean('Light Settings', 'zone_state')

    if party_mode:
        update_bulb_party()
        sleep(float(_screen.update))
    else:
        results = img_proc.screen_avg(_screen)
        rgb = results['rgb']
        dark_ratio = results['dark_ratio']
        try:
            print '\n'
            if zone_mode:
                print 'Parse Method: Zones | Color Mode: %s' % _screen.mode
                for zone in results['zones']:
                    brightness = utility.get_brightness(_screen, zone['dark_ratio'])
                    for bulb in zone['bulbs']:
                        hue_interface.send_rgb_to_bulb(bulb, zone['rgb'], brightness)
            else:
                print 'Parse Method: Standard | Color Mode: %s' % _screen.mode
                update_bulbs(rgb, dark_ratio)
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass


def save_new_preset():
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())

    ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    autostart = config.get('Configuration', 'auto_start')

    all_lights = config.get('Light Settings', 'all_lights')
    active = config.get('Light Settings', 'active')
    update = config.get('Light Settings', 'update')
    update_buffer = config.get('Light Settings', 'update_buffer')
    default = config.get('Light Settings', 'default')
    max_bri = config.get('Light Settings', 'max_bri')
    min_bri = config.get('Light Settings', 'min_bri')
    zones = config.get('Light Settings', 'zones')
    zone_state = config.get('Light Settings', 'zone_state')
    black_rgb = config.get('Light Settings', 'black_rgb')
    display_index = config.get('Light Settings', 'display_index')

    party_mode = config.get('Party Mode', 'running')

    app_state = config.get('App State', 'running')

    json_to_write = {
        'ip': ip,
        'username': username,
        'autostart': autostart,
        'all_lights': all_lights,
        'active': active,
        'update': update,
        'update_buffer': update_buffer,
        'default': default,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'zones': zones,
        'zone_state': zone_state,
        'black_rgb': black_rgb,
        'display_index': display_index,
        'party_mode': party_mode,
        'app_state': app_state
    }

    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = current_path + '\\presets.json'
    if os.path.isfile(filepath):
        with open(filepath) as data_file:
            data = json.load(data_file)

        preset_number = 0
        for key in data:
            preset_number = int(key[-1])

        preset_number = str(preset_number + 1)
        new_key = 'preset_%s' % preset_number
        data[new_key] = json_to_write
        data[new_key]['preset_name'] = 'Preset %s' % preset_number
        data[new_key]['preset_number'] = int(preset_number)
    else:
        json_to_write['preset_name'] = 'Preset 1'
        json_to_write['preset_number'] = 1
        data = {
            'preset_1': json_to_write
        }

    # Write/Rewrite presets.json with new section
    with open(filepath, 'w') as data_file:
        json.dump(data, data_file)

    print '\nSaved new Preset!'


def delete_preset(preset_number):
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = current_path + '\\presets.json'
    with open(filepath) as data_file:
        presets = json.load(data_file)
        key = 'preset_' + str(preset_number)
        del presets[key]

    with open(filepath, 'w') as f:
        json.dump(presets, f)

    print '\nDeleted Preset!'
