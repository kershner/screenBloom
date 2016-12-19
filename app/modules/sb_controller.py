from beautifulhue.api import Bridge
from func_timer import func_timer
import system_monitoring
from time import sleep
import hue_interface
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
                 black_rgb, display_index, party_mode, system_monitoring_enabled,
                 system_monitoring_mode, system_monitoring_interval, color_mode_enabled):
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
        self.system_monitoring_enabled = system_monitoring_enabled
        self.system_monitoring_mode = system_monitoring_mode
        self.system_monitoring_interval = system_monitoring_interval
        self.color_mode_enabled = color_mode_enabled
        self.ohm_interface = {}
        self.wmi_stagger = 10
        self.current_monitoring_loop = 1


def start():
    print '\nHello!'

    # Grab attributes from config file
    atr = initialize()
    global _screen
    _screen = Screen(*atr)

    global t
    t = ScreenBloom(_screen.update)
    t.start()


def stop():
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not running'


def get_screen_object():
    global _screen
    return _screen


# Grab attributes for screen instance
def initialize():
    config_dict = utility.get_config_dict()

    ip = config_dict['ip']
    username = config_dict['username']
    bridge = Bridge(device={'ip': ip}, user={'name': username})

    max_bri = config_dict['max_bri']
    min_bri = config_dict['min_bri']

    active_lights = [int(i) for i in config_dict['active'].split(',')]
    all_lights = [int(i) for i in config_dict['all_lights'].split(',')]

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

    bulb_settings = json.loads(config_dict['bulb_settings'])

    update = config_dict['update']
    update_buffer = config_dict['update_buffer']

    default = [int(i) for i in config_dict['default'].split(',')]
    black_rgb = [int(i) for i in config_dict['black_rgb'].split(',')]

    zones = ast.literal_eval(config_dict['zones'])
    zone_state = bool(config_dict['zone_state'])

    party_mode = bool(config_dict['party_mode'])
    display_index = config_dict['display_index']

    color_mode_enabled = config_dict['color_mode_enabled']
    color_mode = config_dict['color_mode']

    system_monitoring_enabled = config_dict['system_monitoring_enabled']
    system_monitoring_mode = config_dict['system_monitoring_mode']
    system_monitoring_interval = config_dict['system_monitoring_interval']

    return bridge, ip, username, bulb_list, bulb_settings, default, default, \
           update, update_buffer, max_bri, min_bri, zones, zone_state, color_mode, \
           black_rgb, display_index, party_mode, system_monitoring_enabled, \
           system_monitoring_mode, system_monitoring_interval, color_mode_enabled


# Get updated attributes, re-initialize screen object
def re_initialize():
    # Attributes
    at = initialize()

    global _screen
    _screen = Screen(*at)

    update_bulb_default()


# Updates Hue bulbs to specified RGB value
def update_bulbs(new_rgb, dark_ratio):
    screen = get_screen_object()
    screen.rgb = new_rgb
    active_bulbs = [bulb for bulb in screen.bulbs if bulb]
    send_light_commands(active_bulbs, new_rgb, dark_ratio)


# Set bulbs to saved default color
def update_bulb_default():
    screen = get_screen_object()
    default_rgb = screen.default[0], _screen.default[1], _screen.default[2]
    active_bulbs = [bulb for bulb in screen.bulbs if bulb]
    send_light_commands(active_bulbs, default_rgb, 0.0)


# Set bulbs to random RGB
def update_bulb_party():
    print '\nParty Mode!'
    screen = get_screen_object()
    active_bulbs = [bulb for bulb in screen.bulbs if bulb]
    party_color = utility.party_rgb()
    send_light_commands(active_bulbs, party_color, 0.0, party=True)


def send_light_commands(bulbs, rgb, dark_ratio, party=False):
    screen = get_screen_object()

    for bulb in bulbs:
        bulb_settings = screen.bulb_settings[unicode(bulb)]
        bulb_max_bri = bulb_settings['max_bri']
        bulb_min_bri = bulb_settings['min_bri']
        bri = utility.get_brightness(screen, bulb_max_bri, bulb_min_bri, dark_ratio)

        if party:
            rgb = utility.party_rgb()
            try:
                bri = random.randrange(int(screen.min_bri), int(bri) + 1)
            except ValueError as e:
                print e
                continue

        hue_interface.send_rgb_to_bulb(bulb, rgb, bri)


# Main loop
@func_timer
def run():
    screen = get_screen_object()
    sleep(float(screen.update_buffer))

    utility.main_loop_readout(screen)

    if screen.color_mode_enabled:
        results = img_proc.screen_avg(screen)
        color_mode_control_flow(results)

    elif screen.party_mode:
        update_bulb_party()
        sleep(float(screen.update))

    if screen.system_monitoring_enabled:  # Adds ~200ms to the loop
        # Initial check to get WMI connection
        if not screen.ohm_interface:
            screen.ohm_interface = system_monitoring.get_ohm_interface()
            screen.ohm_interface.sample()

        if screen.current_monitoring_loop == screen.wmi_stagger:
            screen.ohm_interface.sample()
            screen.current_monitoring_loop = 1

        system_info = system_monitoring.get_system_temps(screen.ohm_interface.current_sample)
        print system_info
        screen.current_monitoring_loop += 1


def color_mode_control_flow(screen_avg_results):
    try:
        # Zone Mode
        if 'zones' in screen_avg_results:
            for zone in screen_avg_results['zones']:
                for bulb in zone['bulbs']:
                    send_light_commands(bulb, zone['rgb'], zone['dark_ratio'])
        # Standard Mode
        else:
            rgb = screen_avg_results['rgb']
            dark_ratio = screen_avg_results['dark_ratio']
            update_bulbs(rgb, dark_ratio)
    except urllib2.URLError:
        print 'Connection timed out, continuing...'
        pass
