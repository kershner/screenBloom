from beautifulhue.api import Bridge
from time import sleep
import hue_interface
import ConfigParser
import threading
import img_proc
import urllib2
import utility
import random
import ast


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
