from beautifulhue.api import Bridge
import ConfigParser
import utility


# Return more detailed information about specified lights
def get_lights_data(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path() + '\\screenbloom_config.cfg')
    all_lights = config.get('Light Settings', 'all_lights')
    all_lights = [int(i) for i in all_lights.split(',')]
    active_bulbs = config.get('Light Settings', 'active')
    active_bulbs = [int(i) for i in active_bulbs.split(',')]

    lights = []

    for counter, light in enumerate(all_lights):
        resource = {
            'which': light
        }
        result = bridge.light.get(resource)

        # Skip unavailable lights
        if type(result['resource']) is dict:
            state = result['resource']['state']['on']
            light_name = result['resource']['name']
            light_data = [light, state, light_name, int(active_bulbs[counter])]
            lights.append(light_data)

    return lights


# Return list of current Hue light IDs
def get_lights_list(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    resource = {
        'which': 'all'
    }
    lights = bridge.light.get(resource)
    lights = lights['resource']

    lights_list = []
    for light in lights:
        try:
            lights_list.append(str(light['id']))
        except Exception as e:
            print '\nWhooooops!'
            print light
            print e
    return lights_list
