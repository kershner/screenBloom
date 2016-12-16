import sb_controller
import hue_interface
import ConfigParser
import utility
import json
import ast
import os


def get_index_data():
    config_dict = utility.get_config_dict()

    state = config_dict['app_state']
    hue_ip = config_dict['ip']
    username = config_dict['username']
    auto_start = config_dict['autostart']
    current_preset = config_dict['current_preset']
    color_mode_enabled = config_dict['color_mode_enabled']

    update = config_dict['update']
    update_buffer = config_dict['update_buffer']
    max_bri = config_dict['max_bri']
    min_bri = config_dict['min_bri']
    bulb_settings = json.loads(config_dict['bulb_settings'])
    default_color = config_dict['default'].split(',')
    black = config_dict['black_rgb'].split(',')
    zones = ast.literal_eval(config_dict['zones'])
    zone_state = config_dict['zone_state']
    color_mode = config_dict['color_mode']
    display_index = config_dict['display_index']

    party_mode = config_dict['party_mode']

    lights = hue_interface.get_lights_data(hue_ip, username)
    for light in lights:
        light.append(int(bulb_settings[unicode(light[0])]['max_bri']))
        light.append(int(bulb_settings[unicode(light[0])]['min_bri']))

    filepath = utility.get_json_filepath()
    presets = []
    if os.path.isfile(filepath):
        with open(filepath) as data_file:
            presets = json.load(data_file)

    icon_size = 10
    if len(lights) > 3:
        icon_size = 4

    system_monitoring_enabled = config_dict['system_monitoring_enabled']
    system_monitoring_mode = config_dict['system_monitoring_mode']
    system_monitoring_interval = config_dict['system_monitoring_interval']

    data = {
        'state': state,
        'auto_start_state': auto_start,
        'color_mode_enabled': color_mode_enabled,
        'update': update,
        'update_buffer': update_buffer,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'default': config_dict['default'],
        'default_color': default_color,
        'black_rgb': black,
        'lights': lights,
        'lights_number': len(lights),
        'icon_size': icon_size,
        'username': username,
        'party_mode': party_mode,
        'zones': zones,
        'zone_state': zone_state,
        'display_index': display_index,
        'presets': presets,
        'current_preset': current_preset,
        'color_mode': color_mode,
        'system_monitoring_enabled': system_monitoring_enabled,
        'system_monitoring_mode': system_monitoring_mode,
        'system_monitoring_interval': system_monitoring_interval
    }
    return data


def start_screenbloom():
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    state = int(config.get('App State', 'running'))
    update = config.get('Light Settings', 'update')
    sb_controller.get_screen_object().bulb_state = 'on'

    if update:
        state = False

    if state:
        message = 'ScreenBloom already running'
    else:
        utility.write_config('App State', 'running', '1')

        global t
        t = sb_controller.ScreenBloom(update)
        t.start()

        print '\nHello!'
        message = 'ScreenBloom thread initialized'

    data = {
        'message': message
    }
    return data


def stop_screenbloom():
    print '\nEnding screenBloom thread...'
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    utility.write_config('App State', 'running', '0')

    # End currently running threads
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not running'

    sb_controller.update_bulb_default()
    data = {
        'message': 'Successfully ended screenBloom thread'
    }
    return data


def restart_check():
    global t
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    update = config.get('Light Settings', 'update')

    try:
        if t.isAlive():
            print 'Restarting thread...'
            t.join()
            sb_controller.re_initialize()
            utility.write_config('App State', 'running', '1')

            t = sb_controller.ScreenBloom(update)
            t.start()

            print '\nHello!'
        else:
            sb_controller.re_initialize()
    except NameError:
        print 'Thread does not exist yet'
        sb_controller.re_initialize()
