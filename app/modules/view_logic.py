import sb_controller
import hue_interface
import utility
import json
import ast


def get_index_data():
    config_dict = utility.get_config_dict()

    hue_ip = config_dict['ip']
    username = config_dict['username']
    auto_start = config_dict['autostart']
    current_preset = config_dict['current_preset']

    update = config_dict['update']
    update_buffer = config_dict['update_buffer']
    max_bri = config_dict['max_bri']
    min_bri = config_dict['min_bri']
    bulb_settings = json.loads(config_dict['bulb_settings'])
    zones = ast.literal_eval(config_dict['zones'])
    zone_state = config_dict['zone_state']
    display_index = config_dict['display_index']
    sat = config_dict['sat']

    party_mode = config_dict['party_mode']

    state = config_dict['app_state']

    lights = hue_interface.get_lights_data(hue_ip, username)
    for light in lights:
        light.append(int(bulb_settings[unicode(light[0])]['max_bri']))
        light.append(int(bulb_settings[unicode(light[0])]['min_bri']))

    presets = utility.get_all_presets()

    icon_size = 10
    if len(lights) > 3:
        icon_size = 4

    data = {
        'auto_start_state': auto_start,
        'update': update,
        'update_buffer': update_buffer,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'default': config_dict['default'],
        'lights': lights,
        'lights_number': len(lights),
        'icon_size': icon_size,
        'username': username,
        'party_mode': party_mode,
        'zones': zones,
        'zone_state': zone_state,
        'display_index': display_index,
        'sat': sat,
        'presets': presets,
        'current_preset': current_preset,
        'state': state,
    }
    return data


def start_screenbloom():
    config = utility.get_config_dict()
    state = config['app_state']
    sb_controller.get_screen_object().bulb_state = 'on'

    if state:
        message = 'ScreenBloom already running'
    else:
        sb_controller.re_initialize()
        sb_controller.start()

        message = 'ScreenBloom Started!'

    data = {
        'message': message
    }
    return data


def stop_screenbloom():
    sb_controller.stop()
    sb_controller.re_initialize()
    sb_controller.update_bulb_default()

    data = {
        'message': 'ScreenBloom stopped'
    }
    return data


def restart_check():
    global t

    try:
        if t.isAlive():
            t.join()
            sb_controller.start()
        else:
            sb_controller.re_initialize()
    except NameError:
        sb_controller.re_initialize()
