import sb_controller
import hue_interface
import ConfigParser
import requests
import utility
import json
import os


# Create config file on first run
def create_config(hue_ip, username):
    config = ConfigParser.RawConfigParser()
    lights = hue_interface.get_lights_list(hue_ip, username)
    active = ','.join([str(0) for light in lights])

    default_bulb_settings = {}
    for light in lights:
        settings = {
            'max_bri': 254,
            'min_bri': 1
        }
        default_bulb_settings[light] = settings

    config.add_section('Configuration')
    config.set('Configuration', 'hue_ip', hue_ip)
    config.set('Configuration', 'username', username)
    config.set('Configuration', 'auto_start', 0)
    config.set('Configuration', 'current_preset', '')
    config.set('Configuration', 'color_mode_enabled', 0)

    config.add_section('Light Settings')
    config.set('Light Settings', 'all_lights', ','.join(lights))
    config.set('Light Settings', 'active', active)
    config.set('Light Settings', 'bulb_settings', json.dumps(default_bulb_settings))
    config.set('Light Settings', 'update', '0.7')
    config.set('Light Settings', 'update_buffer', '0')
    config.set('Light Settings', 'default', '255,226,168')
    config.set('Light Settings', 'max_bri', '254')
    config.set('Light Settings', 'min_bri', '1')
    config.set('Light Settings', 'zones', '[]')
    config.set('Light Settings', 'zone_state', 0)
    config.set('Light Settings', 'black_rgb', '1,1,1')
    config.set('Light Settings', 'display_index', 0)
    config.set('Light Settings', 'color_mode', 'average')

    config.add_section('System Monitoring')
    config.set('System Monitoring', 'enabled', 0)
    config.set('System Monitoring', 'mode', 'extreme')
    config.set('System Monitoring', 'interval', 5)
    config.set('System Monitoring', 'cpu_warning_temp', 50)
    config.set('System Monitoring', 'cpu_extreme_temp', 70)
    config.set('System Monitoring', 'cpu_warning_color', '255,165,0')
    config.set('System Monitoring', 'cpu_extreme_color', '255,0,0')
    config.set('System Monitoring', 'gpu_warning_temp', 80)
    config.set('System Monitoring', 'gpu_extreme_temp', 95)
    config.set('System Monitoring', 'gpu_warning_color', '255,165,0')
    config.set('System Monitoring', 'gpu_extreme_color', '255,0,0')

    config.add_section('Party Mode')
    config.set('Party Mode', 'running', '0')

    with open(utility.get_config_path(), 'wb') as config_file:
        config.write(config_file)


def remove_config():
    file_path = utility.get_config_path()
    success = True

    try:
        os.remove(file_path)
    except Exception as e:
        success = False

    return success


def register_logic(ip, host):
    if not ip:
        print 'Hue IP not entered manually'
        # Attempting to grab IP from Philips uPNP app
        try:
            print 'Attempting to grab bridge IP...'
            requests.packages.urllib3.disable_warnings()
            url = 'https://www.meethue.com/api/nupnp'
            r = requests.get(url, verify=False).json()
            ip = str(r[0]['internalipaddress'])
            print 'Success!  Hue IP: %s' % ip
        except Exception as e:
            utility.write_traceback()
            error_type = 'manual'
            error_description = 'Error grabbing Hue IP, redirecting to manual entry...'
            data = {
                'success': False,
                'error_type': error_type,
                'error_description': error_description,
                'host': host
            }
            return data
    try:
        print 'Attempting to register app with Hue bridge...'
        # Send post request to Hue bridge to register new username, return response as JSON
        result = register_device(ip)
        temp_result = result[0]
        result_type = ''
        for k, v in temp_result.items():
            result_type = str(k)
        if result_type == 'error':
            error_type = result[0]['error']['type']
            error_description = result[0]['error']['description']
            data = {
                'success': False,
                'error_type': str(error_type),
                'error_description': str(error_description)
            }
            return data
        else:
            print 'Success!  Creating config file...'
            username = temp_result[result_type]['username']
            create_config(ip, username)
            sb_controller.start()
            data = {
                'success': True,
                'message': 'Success!'
            }
            return data
    except requests.exceptions.ConnectionError:
        data = {
            'success': False,
            'error_type': 'Invalid URL',
            'error_description': 'Something went wrong with the connection, please try again...'
        }
        return data
    except IOError:
        data = {
            'success': False,
            'error_type': 'permission',
            'error_description': 'Permission denied, administrator rights needed..'
        }
        return data


# Add username to bridge whitelist
def register_device(hue_ip):
    url = 'http://%s/api/' % hue_ip
    data = {
        'devicetype': 'ScreenBloom'
    }
    body = json.dumps(data)
    r = requests.post(url, data=body, timeout=5)
    return r.json()
