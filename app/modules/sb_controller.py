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
        hue_interface.lights_on_off('On')
        while not self.stoprequest.isSet():
            run()
            sleep(.01)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloom, self).join(timeout)


# Class for Screen object to hold values during runtime
class Screen(object):
    def __init__(self, bridge, ip, devicename, bulbs, bulb_settings, default, rgb, update,
                 update_buffer, max_bri, min_bri, zones, zone_state, mode,
                 black_rgb, display_index, party_mode):
        self.bridge = bridge
        self.ip = ip
        self.devicename = devicename
        self.bulbs = bulbs
        self.bulb_settings = bulb_settings
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
        self.party_mode = party_mode


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

    bulb_settings = json.loads(config.get('Light Settings', 'bulb_settings'))

    update = config.get('Light Settings', 'update')
    update_buffer = config.get('Light Settings', 'update_buffer')

    default = config.get('Light Settings', 'default').split(',')
    default = (int(default[0]), int(default[1]), int(default[2]))

    zones = config.get('Light Settings', 'zones')
    zones = ast.literal_eval(zones)

    zone_state = config.getboolean('Light Settings', 'zone_state')
    party_mode = config.getboolean('Party Mode', 'running')

    # mode = 'dominant'
    mode = 'average'

    black_rgb = config.get('Light Settings', 'black_rgb').split(',')
    black_rgb = (int(black_rgb[0]), int(black_rgb[1]), int(black_rgb[2]))

    display_index = config.get('Light Settings', 'display_index')

    return bridge, ip, username, bulb_list, bulb_settings, default, default, \
           update, update_buffer, max_bri, min_bri, zones, zone_state, mode, \
           black_rgb, display_index, party_mode


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
        if 'zones' in results:
            for zone in results['zones']:
                brightness = utility.get_brightness(_screen, int(_screen.max_bri), int(_screen.min_bri), zone['dark_ratio'])

                for bulb in zone['bulbs']:
                    hue_interface.send_rgb_to_bulb(bulb, zone['rgb'], brightness)
        else:
            update_bulbs(results['rgb'], results['dark_ratio'])
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass


# Updates Hue bulbs to specified RGB value
def update_bulbs(new_rgb, dark_ratio):
    global _screen
    send_light_commands(new_rgb, dark_ratio)
    _screen.rgb = new_rgb


# Set bulbs to saved default color
def update_bulb_default():
    global _screen
    default_rgb = _screen.default[0], _screen.default[1], _screen.default[2]
    send_light_commands(default_rgb, 0.0)


# Set bulbs to random RGB
def update_bulb_party():
    global _screen
    print '\nParty Mode!'
    party_color = utility.party_rgb()
    send_light_commands(party_color, 0.0, party=True)


def send_light_commands(rgb, dark_ratio, party=False):
    global _screen

    active_bulbs = [bulb for bulb in _screen.bulbs if bulb]
    for bulb in active_bulbs:
        bulb_settings = _screen.bulb_settings[unicode(bulb)]
        bulb_max_bri = bulb_settings['max_bri']
        bulb_min_bri = bulb_settings['min_bri']
        bri = utility.get_brightness(_screen, bulb_max_bri, bulb_min_bri, dark_ratio)

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

    if _screen.party_mode:
        update_bulb_party()
        sleep(float(_screen.update))
    else:
        results = img_proc.screen_avg(_screen)

        try:
            print '\n'
            if 'zones' in results:
                print 'Parse Method: zones | Color Mode: %s' % _screen.mode
                for zone in results['zones']:

                    for bulb in zone['bulbs']:
                        bulb_settings = _screen.bulb_settings[unicode(bulb)]
                        bulb_max_bri = bulb_settings['max_bri']
                        bulb_min_bri = bulb_settings['min_bri']
                        bri = utility.get_brightness(_screen, bulb_max_bri, bulb_min_bri, zone['dark_ratio'])
                        hue_interface.send_rgb_to_bulb(bulb, zone['rgb'], bri)
            else:
                print 'Parse Method: standard | Color Mode: %s' % _screen.mode
                rgb = results['rgb']
                dark_ratio = results['dark_ratio']
                update_bulbs(rgb, dark_ratio)
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass


def save_new_preset():
    json_to_write = utility.get_config_dict()
    fa_icons = utility.get_fa_class_names()
    icon = random.choice(fa_icons)

    if os.path.isfile(utility.get_json_filepath()):
        with open(utility.get_json_filepath()) as data_file:
            presets = json.load(data_file)

        preset_number = 0
        for key in presets:
            new_preset_number = int(key[key.find('_') + 1:])
            if new_preset_number > preset_number:
                preset_number = new_preset_number
        preset_number = str(preset_number + 1)
        new_key = 'preset_%s' % preset_number
        presets[new_key] = json_to_write
        presets[new_key]['preset_name'] = 'Preset %s' % preset_number
        presets[new_key]['preset_number'] = int(preset_number)
        presets[new_key]['icon_class'] = icon
    else:
        preset_name = 'preset_1'
        preset_number = 1
        json_to_write['preset_name'] = 'Preset 1'
        json_to_write['preset_number'] = preset_number
        json_to_write['icon_class'] = icon
        presets = {
            preset_name: json_to_write
        }

    # Write/Rewrite presets.json with new section
    with open(utility.get_json_filepath(), 'w') as data_file:
        json.dump(presets, data_file)

    print '\nSaved new Preset!'
    return preset_number


def delete_preset(preset_number):
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    current_preset = config.get('Configuration', 'current_preset')

    with open(utility.get_json_filepath()) as data_file:
        presets = json.load(data_file)
        key = 'preset_' + str(preset_number)

        if presets[key]['preset_name'] == current_preset:
            utility.write_config('Configuration', 'current_preset', '')

        del presets[key]

    with open(utility.get_json_filepath(), 'w') as f:
        json.dump(presets, f)

    print '\nDeleted Preset!'


def apply_preset(preset_number):
    with open(utility.get_json_filepath()) as data_file:
        presets = json.load(data_file)

    preset_index = 'preset_' + str(preset_number)
    preset = presets[preset_index]
    utility.write_config('Light Settings', 'min_bri', preset['min_bri'])
    utility.write_config('Light Settings', 'max_bri', preset['max_bri'])
    utility.write_config('Light Settings', 'black_rgb', preset['black_rgb'])
    utility.write_config('Light Settings', 'update', preset['update'])
    utility.write_config('Light Settings', 'update_buffer', preset['update_buffer'])
    utility.write_config('Light Settings', 'default', preset['default'])
    utility.write_config('Party Mode', 'running', preset['party_mode'])
    utility.write_config('Configuration', 'auto_start', preset['autostart'])
    utility.write_config('Light Settings', 'zone_state', preset['zone_state'])
    utility.write_config('Light Settings', 'zones', preset['zones'])
    utility.write_config('Light Settings', 'active', preset['active'])
    utility.write_config('Light Settings', 'bulb_settings', preset['bulb_settings'])
    utility.write_config('Light Settings', 'display_index', preset['display_index'])
    return preset


def update_preset(preset_number, preset_name, icon):
    with open(utility.get_json_filepath()) as data_file:
        presets = json.load(data_file)

    preset_to_edit = None
    for preset in presets:
        if int(preset_number) == presets[preset]['preset_number']:
            preset_to_edit = preset
            print preset_to_edit

    preset_number = presets[preset_to_edit]['preset_number']
    presets[preset_to_edit] = utility.get_config_dict()
    presets[preset_to_edit]['preset_name'] = preset_name
    presets[preset_to_edit]['icon_class'] = icon
    presets[preset_to_edit]['preset_number'] = preset_number

    with open(utility.get_json_filepath(), 'w') as f:
        json.dump(presets, f)

    print '\nUpdated Preset!'
