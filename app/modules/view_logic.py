from colour import Color
import sb_controller
import hue_interface
import utility
import json
import ast
import os


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

    # This is pretty ghetto ################################################
    monitoring_setting_types = ['CPU', 'GPU']
    system_monitoring_settings = []
    for setting_type in monitoring_setting_types:
        warning_c = config_dict['%s_warning_color' % setting_type.lower()].split(',')
        extreme_c = config_dict['%s_extreme_color' % setting_type.lower()].split(',')
        warning_color = Color(rgb=(int(warning_c[0]) / 255.0, int(warning_c[1]) / 255.0, int(warning_c[2]) / 255.0)).hex
        extreme_color = Color(rgb=(int(extreme_c[0]) / 255.0, int(extreme_c[1]) / 255.0, int(extreme_c[2]) / 255.0)).hex

        formatted_type = {
            'type': setting_type,
            'name': 'Some BS',
            'warning_temp': config_dict['%s_warning_temp' % setting_type.lower()],
            'extreme_temp': config_dict['%s_extreme_temp' % setting_type.lower()],
            'warning_color': warning_color,
            'extreme_color': extreme_color,
        }
        system_monitoring_settings.append(formatted_type)
    # end pretty ghetto stuff ##############################################

    data = {
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
        'system_monitoring_interval': system_monitoring_interval,
        'system_monitoring_settings': system_monitoring_settings
    }
    return data


def start_screenbloom():
    config = utility.get_config_dict()
    state = config['color_mode_enabled']
    sb_controller.get_screen_object().bulb_state = 'on'

    if state:
        message = 'ScreenBloom already running'
    else:
        utility.write_config('Configuration', 'color_mode_enabled', True)
        sb_controller.re_initialize()

        message = 'Color Mode Started!'

    data = {
        'message': message
    }
    return data


def stop_screenbloom():
    utility.write_config('Configuration', 'color_mode_enabled', False)
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
            print '\nRestarting thread...'
            t.join()
            sb_controller.start()
        else:
            sb_controller.re_initialize()
    except NameError:
        # print '\nThread does not exist yet'
        sb_controller.re_initialize()
