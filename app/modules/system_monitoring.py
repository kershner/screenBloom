from vendor.wmi import sampler
import logging


def get_ohm_interface():
    return sampler.WMISampler(logging.getLogger(), 'Sensor', ['name', 'value'], namespace='root\OpenHardwareMonitor')


# Grab all kinds of good system info from Open Hardware Monitor
def get_system_temps(sensor_sample):
    cpu_temps = {}
    gpu_temps = {}
    count = 1

    sorted_sensor_sample = sorted(sensor_sample, key=lambda k: k['value'], reverse=True)
    for entry in sorted_sensor_sample:
        name = entry['name']
        value = entry['value']

        if value == 0.0:
            continue
        elif value > 1000:
            continue
        elif 'Core' not in name:
            continue
        elif 'GPU' not in name and 'CPU' not in name:
            continue

        # print entry
        if 'CPU Cores' in entry['name']:
            continue
        if 'CPU Core' in entry['name']:
            if not entry['name'] in cpu_temps:  # Grab 2nd CPU Core values
                cpu_temps[entry['name']] = entry['value']
        if 'GPU Core' in entry['name']:
            key = entry['name'] + '_' + str(count)
            gpu_temps[key] = entry['value']
            count += 1

    sorted_gpu_temp = sorted(gpu_temps, key=lambda k: k[1])
    try:
        gpu_temp = gpu_temps[sorted_gpu_temp[1]]
    except IndexError:
        try:
            gpu_temp = gpu_temps[sorted_gpu_temp[0]]
        except IndexError:
            print 'No results, Open Hardware Monitor is probably not running...'
            return {}

    if gpu_temp < 10:
        gpu_temp = None

    temps = {
        'cpu_temps': cpu_temps,
        'gpu_temp': gpu_temp
    }

    return temps
