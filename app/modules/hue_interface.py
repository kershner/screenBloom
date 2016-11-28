from beautifulhue.api import Bridge
import vendor.rgb_xy as rgb_xy
import sb_controller
import ConfigParser
import utility


# Return more detailed information about specified lights
def get_lights_data(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
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
            model_id = result['resource']['modelid']
            light_data = [light, state, light_name, int(active_bulbs[counter]), model_id]
            lights.append(light_data)

    print lights
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


# Send on/off Hue API command to bulbs
def lights_on_off(state):
    print '\nTurning Selected Lights %s' % state

    _screen = sb_controller.get_screen_object()

    active_lights = _screen.bulbs
    state = True if state == 'On' else False

    for light in active_lights:
        resource = {
            'which': light,
            'data': {
                'state': {
                    'on': state,
                    'bri': int(_screen.max_bri),
                    'transitiontime': _screen.update
                }
            }
        }
        _screen.bridge.light.update(resource)


# Sends Hue API command to bulb
def send_rgb_to_bulb(bulb, rgb, brightness):
    _screen = sb_controller.get_screen_object()
    if bulb:  # Only contact active lights
        print 'Updating Bulb: %s -> Color: %s | Bri: %s' % (str(bulb), str(rgb), str(brightness))

        if int(brightness) < 5:  # Maybe set user controlled darkness threshold here?
            rgb = _screen.black_rgb

        # Need to determine which gamut to use here
        converter = rgb_xy.Converter()
        hue_color = converter.rgb_to_xy(rgb[0], rgb[1], rgb[2])
        resource = {
            'which': bulb,
            'data': {
                'state': {
                    'xy': hue_color,
                    'bri': int(brightness),
                    'transitiontime': utility.get_transition_time(_screen.update)
                }
            }
        }
        _screen.bridge.light.update(resource)
