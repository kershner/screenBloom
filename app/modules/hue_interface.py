from beautifulhue.api import Bridge
import vendor.rgb_xy as rgb_xy
import sb_controller
import utility


# Return more detailed information about specified lights
def get_lights_data(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    config = utility.get_config_dict()

    all_lights = [int(i) for i in config['all_lights'].split(',')]
    active_bulbs = [int(i) for i in config['active'].split(',')]
    lights = []

    for counter, light in enumerate(all_lights):
        resource = {
            'which': light
        }
        result = bridge.light.get(resource)

        if type(result['resource']) is dict:  # Skip unavailable lights
            state = result['resource']['state']['on']
            light_name = result['resource']['name']
            model_id = result['resource']['modelid']
            bri = result['resource']['state']['bri']
            xy = result['resource']['state']['xy']

            try:
                colormode = result['resource']['state']['colormode']
            except KeyError:
                colormode = None

            active = light if int(light) in active_bulbs else 0
            light_data = [light, state, light_name, active, model_id, bri, xy, colormode]

            lights.append(light_data)

    return lights


def get_light_diagnostic_data(hue_ip, username):
    bridge = Bridge(device={'ip': hue_ip}, user={'name': username})
    config = utility.get_config_dict()

    all_lights = [int(i) for i in config['all_lights'].split(',')]
    lights = {}

    for counter, light in enumerate(all_lights):
        resource = {
            'which': light
        }
        result = bridge.light.get(resource)
        lights[light] = result

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
        except Exception:
            pass

    return lights_list


# Send on/off Hue API command to bulbs
def lights_on_off(state):
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
def send_rgb_or_xy_to_bulb(bulb, rgb_or_xy, brightness):
    _screen = sb_controller.get_screen_object()
    bulb_settings = _screen.bulb_settings[str(bulb)]
    bulb_gamut = bulb_settings['gamut']
    gamut = get_rgb_xy_gamut(bulb_gamut)
    converter = rgb_xy.Converter(gamut)

    resource = {
        'which': bulb,
        'data': {
            'state': {
                'bri': int(brightness),
                'transitiontime': utility.get_transition_time(_screen.update)
            }
        }
    }

    if rgb_or_xy:
        if len(rgb_or_xy) > 2:  # [R, G, B] vs [X, Y]
            try:
                hue_color = converter.rgb_to_xy(rgb_or_xy[0], rgb_or_xy[1], rgb_or_xy[2])
            except ZeroDivisionError:
                return
        else:
            hue_color = (rgb_or_xy[0], rgb_or_xy[1])

        resource['data']['state']['xy'] = hue_color

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
