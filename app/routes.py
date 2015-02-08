from flask import Flask, render_template, jsonify, request, redirect, url_for
import screenbloom
import threading
import sys
import ssdp

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/hue-config')
def hue_config():
    screenbloom.print_hue_config()

    data = {'hello': 'hello!'}

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

    screenbloom.register_device(hue_ip, username)
    screenbloom.create_config(hue_ip, username)

    data = {
        'link': '/'
    }

    return jsonify(data)


@app.route('/update-config')
def update_config():
    sat = request.args.get('sat', 0, type=str)
    bri = request.args.get('bri', 0, type=str)
    transition = request.args.get('transition', 0, type=str)

    try:
        if t.isAlive():
            print 'Thread is running!'
            t.join()
            screenbloom.write_config(sat, bri, transition, 'False', 'False')
            screenbloom.re_initialize()

            return redirect(url_for('start'))
        else:
            screenbloom.write_config(sat, bri, transition, 'False', 'False')
            screenbloom.re_initialize()
            print 'Thread is not running!'
    except NameError:
        print 't not defined yet!'
        screenbloom.write_config(sat, bri, transition, 'False', 'False')
        screenbloom.re_initialize()

    data = {
        'message': 'Updated config file!'
    }

    return jsonify(data)


@app.route('/')
def index():
    global startup_thread
    if startup_thread.is_alive():
        startup_thread.join()
        print 'Running threads: '
        print threading.enumerate()

    config = screenbloom.config_to_list()
    screenbloom.write_config(config[3], config[4], config[5], config[6], 'False')

    sat = config[3]
    bri = config[4]
    transition = config[5]

    return render_template('/home.html',
                           sat=sat,
                           bri=bri,
                           transition=transition)


@app.route('/start')
def start():
    print 'Firing run function...'

    config = screenbloom.config_to_list()
    trans = config[5]
    running = config[6]
    if running == 'True':
        data = {
            'message': 'ScreenBloom already running'
        }

        return jsonify(data)
    else:
        # Rewriting config file with 'Running = True' value
        screenbloom.write_config(config[3], config[4], trans, 'True', 'False')

        global t
        t = screenbloom.ScreenBloomThread(trans)
        t.start()

        print 'Hello!'

        data = {
            'message': 'ScreenBloom thread initialized'
        }

        return jsonify(data)


@app.route('/stop')
def stop():
    print 'Ending screenBloom thread...'

    # Rewriting config file with 'Running = False' value
    config = screenbloom.config_to_list()
    screenbloom.write_config(config[3], config[4], config[5], 'False', 'True')

    # End currently running threads
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not running'

    # Update bulbs to a normal white color
    screenbloom.update_bulb_default()

    data = {
        'message': 'Successfully ended screenBloom thread'
    }

    return jsonify(data)


@app.route('/get-settings')
def get_settings():
    config = screenbloom.config_to_list()

    data = {
        'bulbs-value': config[2],
        'sat-value': config[3],
        'bri-value': config[4],
        'trans-value': config[5],
        'running-state': config[6]
    }

    return jsonify(data)


@app.route('/end-app')
def end_app():
    config = screenbloom.config_to_list()
    screenbloom.write_config(config[3], config[4], config[5], 'False', 'True')

    print 'Ending threads and closing ScreenBloom...'
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not currently running'

    sys.exit()


if __name__ == '__main__':
    local_host = '192.168.0.5'
    # local_host = '127.0.0.1'

    startup_thread = screenbloom.StartupThread(local_host)
    startup_thread.start()

    app.run(debug=True, host=local_host, use_reloader=False)