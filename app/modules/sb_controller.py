from beautifulhue.api import Bridge
from time import sleep
import hue_interface
import ConfigParser
import threading
import urllib2
import utility
import random
import json
import ast

if utility.dll_check():
    import img_proc


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
                 update_buffer, max_bri, min_bri, zones, zone_state, color_mode,
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
        self.color_mode = color_mode
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

    black_rgb = config.get('Light Settings', 'black_rgb').split(',')
    black_rgb = (int(black_rgb[0]), int(black_rgb[1]), int(black_rgb[2]))

    display_index = config.get('Light Settings', 'display_index')

    color_mode = config.get('Light Settings', 'color_mode')

    return bridge, ip, username, bulb_list, bulb_settings, default, default, \
           update, update_buffer, max_bri, min_bri, zones, zone_state, color_mode, \
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
                print 'Parse Method: zones | Color Mode: %s' % _screen.color_mode
                for zone in results['zones']:

                    for bulb in zone['bulbs']:
                        bulb_settings = _screen.bulb_settings[unicode(bulb)]
                        bulb_max_bri = bulb_settings['max_bri']
                        bulb_min_bri = bulb_settings['min_bri']
                        bri = utility.get_brightness(_screen, bulb_max_bri, bulb_min_bri, zone['dark_ratio'])
                        hue_interface.send_rgb_to_bulb(bulb, zone['rgb'], bri)
            else:
                print 'Parse Method: standard | Color Mode: %s' % _screen.color_mode
                rgb = results['rgb']
                dark_ratio = results['dark_ratio']
                update_bulbs(rgb, dark_ratio)
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass
