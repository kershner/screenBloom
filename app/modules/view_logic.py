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
    color_mode_enabled = config_dict['color_mode_enabled']

    update = config_dict['update']
    update_buffer = config_dict['update_buffer']
    max_bri = config_dict['max_bri']
    min_bri = config_dict['min_bri']
    bulb_settings = json.loads(config_dict['bulb_settings'])
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

    presets = utility.get_all_presets()

    icon_size = 10
    if len(lights) > 3:
        icon_size = 4

    data = {
        'auto_start_state': auto_start,
        'color_mode_enabled': color_mode_enabled,
        'update': update,
        'update_buffer': update_buffer,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'default': config_dict['default'],
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
        'color_mode': color_mode
    }
    return data


def start_screenbloom():
    config = utility.get_config_dict()
    state = config['color_mode_enabled']
    sb_controller.get_screen_object().bulb_state = 'on'
    hue_interface.lights_on_off('On')

    if state:
        message = 'ScreenBloom already running'
    else:
        utility.write_config('Configuration', 'color_mode_enabled', True)
        sb_controller.re_initialize()
        sb_controller.start()

        message = 'Color Mode Started!'

    data = {
        'message': message
    }
    return data


def stop_screenbloom():
    utility.write_config('Configuration', 'color_mode_enabled', False)
    sb_controller.stop()
    sb_controller.re_initialize()
    sb_controller.update_bulb_default()

    data = {
        'message': 'Color Mode stopped'
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
