import ConfigParser
import utility
import random
import json
import os


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
    utility.write_config('Light Settings', 'color_mode', preset['color_mode'])
    return preset


def update_preset(preset_number, preset_name, icon):
    with open(utility.get_json_filepath()) as data_file:
        presets = json.load(data_file)

    preset_to_edit = None
    for preset in presets:
        if int(preset_number) == presets[preset]['preset_number']:
            preset_to_edit = preset

    preset_number = presets[preset_to_edit]['preset_number']
    presets[preset_to_edit] = utility.get_config_dict()
    presets[preset_to_edit]['preset_name'] = preset_name
    presets[preset_to_edit]['icon_class'] = icon
    presets[preset_to_edit]['preset_number'] = preset_number

    with open(utility.get_json_filepath(), 'w') as f:
        json.dump(presets, f)

    print '\nUpdated Preset!'
