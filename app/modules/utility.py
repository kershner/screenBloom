from desktopmagic.screengrab_win32 import getDisplaysAsImages
from config import params
from PIL import ImageGrab
import ConfigParser
import traceback
import requests
import StringIO
import random
import sys
import os


def get_config_path():
    config_path = ''

    if params.BUILD == 'win':
        config_path = os.getenv('APPDATA')
    elif params.BUILD == 'mac':
        config_path = ''
        if getattr(sys, 'frozen', False):
            config_path = os.path.dirname(sys.executable)
        elif __file__:
            config_path = os.path.dirname(__file__)

    return config_path


# Check server status
def check_server(host):
    try:
        r = requests.get('http://%s:5000/new-user' % host)
        response = r.status_code
    except requests.ConnectionError:
        response = 404
    if response == 200:
        return True
    else:
        return False


# Rewrite config file with given arguments
def write_config(section, item, value):
    config = ConfigParser.RawConfigParser()
    config.read(get_config_path() + '\\screenbloom_config.cfg')
    config.set(section, item, value)

    with open(get_config_path() + '\\screenbloom_config.cfg', 'wb') as config_file:
        config.write(config_file)


# Write traceback to logfile
def write_traceback():
    with open('log.txt', 'a+') as f:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=f)


# Generate truly random RGB
def party_rgb():
    r = lambda: random.randint(0, 255)
    rgb = (r(), r(), r())
    return rgb


def get_screenshot():
    img = ImageGrab.grab()
    tmp = StringIO.StringIO()
    img.save(tmp, format="PNG")
    b64_data = tmp.getvalue().encode('base64')
    return b64_data


def get_multi_monitor_screenshots():
    imgs = getDisplaysAsImages()
    screenshots = []

    for img in imgs:
        tmp = StringIO.StringIO()
        img.save(tmp, format="PNG")
        b64_data = tmp.getvalue().encode('base64')
        screenshots.append(b64_data)

    return screenshots


def display_check(_screen):
    displays = getDisplaysAsImages()
    try:
        displays[int(_screen.display_index)]
    except IndexError as e:
        print 'Can\'t find display index, switching to default'
        write_config('Light Settings', 'display_index', 0)
        _screen.display_index = 0
    return
