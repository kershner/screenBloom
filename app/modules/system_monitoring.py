from vendor.wmi import sampler
from colour import Color
import logging


def get_ohm_interface():
    return sampler.WMISampler(logging.getLogger(), 'Sensor', ['name', 'value'], namespace='root\OpenHardwareMonitor')


# Grab all kinds of good system info from Open Hardware Monitor
def get_system_temps(sensor_sample):
    cpu_packages = []
    gpu_cores = []

    sorted_sensor_sample = sorted(sensor_sample, key=lambda k: k['instanceid'], reverse=True)
    for entry in sorted_sensor_sample:
        name = entry['name']
        value = entry['value']

        if value == 0.0:
            continue
        elif value > 1000:
            continue
        elif 'GPU' not in name and 'CPU' not in name:
            continue

        if name == 'CPU Package':
            cpu_packages.append(value)
        if name == 'GPU Core':
            gpu_cores.append(value)

    try:
        temps = {
            'cpu_temp': cpu_packages[1],
            'gpu_temp': gpu_cores[2]
        }
    except IndexError as e:
        print 'No results, Open Hardware Monitor is probably not running.'
        temps = {}

    return temps


def get_temp_color_ranges(config):
    cpu_warning_temp = config['cpu_warning_temp']
    cpu_extreme_temp = config['cpu_extreme_temp']
    gpu_warning_temp = config['gpu_warning_temp']
    gpu_extreme_temp = config['gpu_extreme_temp']

    cpu_warning_color = get_rgb_tuple(config['cpu_warning_color'])
    cpu_extreme_color = get_rgb_tuple(config['cpu_extreme_color'])
    gpu_warning_color = get_rgb_tuple(config['gpu_warning_color'])
    gpu_extreme_color = get_rgb_tuple(config['gpu_extreme_color'])

    cpu_warning_color = Color(rgb=(cpu_warning_color[0], cpu_warning_color[1], cpu_warning_color[2]))
    cpu_extreme_color = Color(rgb=(cpu_extreme_color[0], cpu_extreme_color[1], cpu_extreme_color[2]))
    gpu_warning_color = Color(rgb=(gpu_warning_color[0], gpu_warning_color[1], gpu_warning_color[2]))
    gpu_extreme_color = Color(rgb=(gpu_extreme_color[0], gpu_extreme_color[1], gpu_extreme_color[2]))

    cpu_temp_range = range(int(cpu_warning_temp), int(cpu_extreme_temp))
    cpu_colors = list(cpu_warning_color.range_to(cpu_extreme_color, len(cpu_temp_range)))

    gpu_temp_range = range(int(gpu_warning_temp), int(gpu_extreme_temp))
    gpu_colors = list(gpu_warning_color.range_to(gpu_extreme_color, len(gpu_temp_range)))

    cpu_color_scale = {}
    for index, temp in enumerate(cpu_temp_range):
        cpu_color_scale[temp] = cpu_colors[index]

    gpu_color_scale = {}
    for index, temp in enumerate(gpu_temp_range):
        gpu_color_scale[temp] = gpu_colors[index]

    return {
        'gpu': gpu_color_scale,
        'cpu': cpu_color_scale
    }


# Check current temps vs user-set thresholds
# Returns color to update bulbs or False
def analyze_temps(screen, system_info):
    temp_color_ranges = screen.temp_color_ranges

    cpu_warning_temp = screen.user_temps['cpu']['warning']
    cpu_extreme_temp = screen.user_temps['cpu']['extreme']
    gpu_warning_temp = screen.user_temps['gpu']['warning']
    gpu_extreme_temp = screen.user_temps['gpu']['extreme']

    current_cpu_temp = system_info['cpu_temp']
    current_gpu_temp = system_info['gpu_temp']

    print '\n///////////////////////////////////'
    print 'Current CPU Temp: ', current_cpu_temp
    print 'Current GPU Temp: ', current_gpu_temp

    # First check CPU temps
    try:
        if current_cpu_temp > cpu_extreme_temp:
            print 'CPU EXTREME'
            return get_full_rgb_tuple(temp_color_ranges['cpu'][current_cpu_temp].rgb)
        elif current_cpu_temp > cpu_warning_temp:
            print 'CPU WARNING'
            return get_full_rgb_tuple(temp_color_ranges['cpu'][current_cpu_temp].rgb)
    except KeyError:
        return get_full_rgb_tuple(temp_color_ranges['cpu'].items()[-1][1].rgb)

    # Next check GPU temps
    try:
        if current_gpu_temp > gpu_extreme_temp:
            print 'GPU EXTREME'
            return get_full_rgb_tuple(temp_color_ranges['gpu'][current_gpu_temp].rgb)
        elif current_gpu_temp > gpu_warning_temp:
            print 'GPU WARNING'
            return get_full_rgb_tuple(temp_color_ranges['gpu'][current_gpu_temp].rgb)
    except KeyError:
        return get_full_rgb_tuple(temp_color_ranges['gpu'].items()[-1][1].rgb)

    return False


def get_rgb_tuple(rgb_string):
    tmp = rgb_string.split(',')
    return int(tmp[0]) / 255.0, int(tmp[1]) / 255.0, int(tmp[2]) / 255.0


def get_full_rgb_tuple(rgb_tuple):
    new_tup = [int(i * 255) for i in rgb_tuple]
    return new_tup[0], new_tup[1], new_tup[2]
