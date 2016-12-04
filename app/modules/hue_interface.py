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
        bulb_settings = _screen.bulb_settings[str(bulb)]
        bulb_gamut = bulb_settings['gamut']
        name = bulb_settings['name']
        gamut = get_rgb_xy_gamut(bulb_gamut)
        converter = rgb_xy.Converter(gamut)
        print 'Updating %s -> Color: rgb%s | Gamut: %s | Bri: %s' % (str(name), str(rgb), str(bulb_gamut), str(brightness))

        if int(brightness) < 5:  # Maybe set user controlled darkness threshold here?
            rgb = _screen.black_rgb

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


def get_rgb_xy_gamut(bulb_gamut):
    if bulb_gamut == 'A':
        return rgb_xy.GamutA
    elif bulb_gamut == 'B':
        return rgb_xy.GamutB
    elif bulb_gamut == 'C':
        return rgb_xy.GamutC


def get_gamut(model_id):
    try:
        gamut = GAMUTS[model_id]['gamut']
    except KeyError:
        gamut = 'B'
    return gamut

# https://developers.meethue.com/documentation/supported-lights
GAMUTS = {
    'LCT001': {
        'name': 'Hue bulb A19',
        'gamut': 'B'
    },
    'LCT007': {
        'name': 'Hue bulb A19',
        'gamut': 'B'
    },
    'LCT010': {
        'name': 'Hue bulb A19',
        'gamut': 'C'
    },
    'LCT014': {
        'name': 'Hue bulb A19',
        'gamut': 'C'
    },
    'LCT002': {
        'name': 'Hue Spot BR30',
        'gamut': 'B'
    },
    'LCT003': {
        'name': 'Hue Spot GU10',
        'gamut': 'B'
    },
    'LCT011': {
        'name': 'Hue BR30',
        'gamut': 'C'
    },
    'LST001': {
        'name': 'Hue LightStrips',
        'gamut': 'A'
    },
    'LLC010': {
        'name': 'Hue Living Colors Iris',
        'gamut': 'A'
    },
    'LLC011': {
        'name': 'Hue Living Colors Bloom',
        'gamut': 'A'
    },
    'LLC012': {
        'name': 'Hue Living Colors Bloom',
        'gamut': 'A'
    },
    'LLC006': {
        'name': 'Living Colors Gen3 Iris*',
        'gamut': 'A'
    },
    'LLC007': {
        'name': 'Living Colors Gen3 Bloom, Aura*',
        'gamut': 'A'
    },
    'LLC013': {
        'name': 'Disney Living Colors',
        'gamut': 'A'
    },
    'LLM001': {
        'name': 'Color Light Module',
        'gamut': 'A'
    },
    'LLC020': {
        'name': 'Hue Go',
        'gamut': 'C'
    },
    'LST002': {
        'name': 'Hue LightStrips Plus',
        'gamut': 'C'
    },
}
