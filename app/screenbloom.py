from flask import Flask, render_template, jsonify, request, redirect, url_for
from modules import ssdp
from modules import screenbloom_functions
import jinja2.ext
import ConfigParser
import requests.exceptions
import threading
import socket
import sys
import os

# app = Flask(__name__)
app = Flask(__name__, static_url_path='', static_folder='', template_folder='')
app.secret_key = os.urandom(24)


# Temp route for development - prints current Hue Lights config.  Useful to see whitelisted usernames.
@app.route('/hue-config')
def hue_config():
    screenbloom_functions.print_hue_config()

    data = {'hello': 'hello!'}

    return jsonify(data)


@app.route('/')
def index():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    global startup_thread
    if startup_thread.is_alive():
        startup_thread.join()
        print 'Running threads: '
        print threading.enumerate()

    screenbloom_functions.write_config('App State', 'user_exit', '0')

    hue_ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    sat = config.get('Light Settings', 'sat')
    bri = config.get('Light Settings', 'bri')
    trans = config.get('Light Settings', 'trans')
    dynamic_bri = config.getboolean('Dynamic Brightness', 'running')
    min_bri = config.get('Dynamic Brightness', 'min_bri')
    lights = screenbloom_functions.get_lights_data(hue_ip, username)

    return render_template('/home.html',
                           sat=sat,
                           bri=bri,
                           transition=trans,
                           dynamic_bri=dynamic_bri,
                           min_bri=min_bri,
                           lights=lights,
                           username=username,
                           title='Home')


@app.route('/start')
def start():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    print 'Firing run function...'

    trans = config.get('Light Settings', 'trans')
    running = config.get('App State', 'running')

    if running == 'True':
        data = {
            'message': 'ScreenBloom already running'
        }

        return jsonify(data)
    else:
        # Rewriting config file with 'Running = True' value
        screenbloom_functions.write_config('App State', 'running', '1')

        global t
        t = screenbloom_functions.ScreenBloomThread(trans)
        t.start()

        print 'Hello!'

        data = {
            'message': 'ScreenBloom thread initialized'
        }

        return jsonify(data)


@app.route('/stop')
def stop():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    print 'Ending screenBloom thread...'

    # Rewriting config file with 'Running = False' value
    screenbloom_functions.write_config('App State', 'running', '0')
    screenbloom_functions.write_config('App State', 'user_exit', '1')

    # End currently running threads
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not running'

    # Update bulbs to a normal white color
    screenbloom_functions.update_bulb_default()

    data = {
        'message': 'Successfully ended screenBloom thread'
    }

    return jsonify(data)


@app.route('/new-user')
def new_user():
    return render_template('/new_user.html',
                           title='New User')


@app.route('/register', methods=['GET', 'POST'])
def register():
    ssdp_response = ssdp.discover('IpBridge')
    hue_ip = str(ssdp_response)[22:33]
    username = request.args.get('username', 0, type=str)

    try:
        # Send post request to Hue bridge to register new username, return response as JSON
        result = screenbloom_functions.register_device(hue_ip, username)
        print result
        temp_result = result[0]
        result_type = ''
        for k, v in temp_result.items():
            result_type = str(k)
        if result_type == 'error':
            error_type = result[0]['error']['type']
            print error_type
            error_description = result[0]['error']['description']

            data = {
                'success': False,
                'error_type': str(error_type),
                'error_description': str(error_description)
            }

            return jsonify(data)
        else:
            screenbloom_functions.create_config(hue_ip, username)

            data = {
                'success': True,
                'message': 'Success!'
            }

            return jsonify(data)
    except requests.exceptions.InvalidURL:
        # InvalidURL error, happens from time to time on localhost
        print 'Something went wrong...'
        data = {
            'success': False,
            'error_type': 'Invalid URL'
        }

        return jsonify(data)


@app.route('/update-config')
def update_config():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')

    sat = request.args.get('sat', 0, type=str)
    bri = request.args.get('bri', 0, type=str)
    trans = request.args.get('transition', 0, type=str)
    active_bulbs = request.args.get('bulbs', 0, type=str)
    dynamic_bri = request.args.get('dynamicBri', 0, type=str)
    min_bri = request.args.get('minBri', 0, type=str)

    settings = [
        ('Light Settings', 'sat', sat),
        ('Light Settings', 'bri', bri),
        ('Light Settings', 'trans', trans),
        ('Light Settings', 'active', active_bulbs),
        ('Dynamic Brightness', 'running', dynamic_bri),
        ('Dynamic Brightness', 'min_bri', min_bri),
        ('App State', 'running', '0'),
        ('App State', 'user_exit', '0')
    ]

    try:
        if t.isAlive():
            print 'Thread is running!'
            t.join()
            settings[6] = ('App State', 'running', '1')
            for s in settings:
                screenbloom_functions.write_config(s[0], s[1], s[2])
            screenbloom_functions.re_initialize()
            return redirect(url_for('start'))
        else:
            print 'Thread is not running!'
            for s in settings:
                screenbloom_functions.write_config(s[0], s[1], s[2])
            screenbloom_functions.re_initialize()
    except NameError:
        print 't not defined yet!'
        for s in settings:
                screenbloom_functions.write_config(s[0], s[1], s[2])
        screenbloom_functions.re_initialize()

    data = {
        'message': 'Updated config file!'
    }

    return jsonify(data)


@app.route('/get-settings')
def get_settings():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    active_lights = config.get('Light Settings', 'active')
    all_lights = config.get('Light Settings', 'all_lights')

    data = {
        'bulbs-value': [int(i) for i in active_lights.split(',')],
        'sat-value': config.get('Light Settings', 'sat'),
        'bri-value': config.get('Light Settings', 'bri'),
        'trans-value': config.get('Light Settings', 'trans'),
        'running-state': config.get('App State', 'running'),
        'all-bulbs': [int(i) for i in all_lights.split(',')],
        'dynamic-brightness': config.getboolean('Dynamic Brightness', 'running'),
        'min-bri': config.get('Dynamic Brightness', 'min_bri')
    }

    return jsonify(data)


@app.route('/end-app')
def end_app():
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    screenbloom_functions.write_config('App State', 'running', '0')
    screenbloom_functions.write_config('App State', 'user_exit', '1')

    print 'Ending threads and closing ScreenBloom...'
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not currently running'

    sys.exit()


if __name__ == '__main__':
    local_host = socket.gethostbyname(socket.gethostname())

    startup_thread = screenbloom_functions.StartupThread(local_host)
    startup_thread.start()

    app.run(debug=True, host=local_host, use_reloader=False)