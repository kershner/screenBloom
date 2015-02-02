from flask import Flask, render_template, jsonify, request, redirect, url_for
import screenbloom
import threading
import time

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


# Class for running screenBloom thread
class ScreenBloomThread(threading.Thread):
    def __init__(self, transition):
        super(ScreenBloomThread, self).__init__()
        self.transition = transition
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.isSet():
            screenbloom.run()

            # 1ms longer than transition time so animations can finish
            transition = (float(self.transition) / 10 + 0.1)
            time.sleep(transition)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(ScreenBloomThread, self).join(timeout)


@app.route('/update-config')
def update_config():
    sat = request.args.get('sat', 0, type=str)
    bri = request.args.get('bri', 0, type=str)
    transition = request.args.get('transition', 0, type=str)

    try:
        if t.isAlive():
            print 'Thread is running!'
            t.join()
            screenbloom.write_config(sat, bri, transition)
            screenbloom.re_initialize()
            return redirect(url_for('start'))
        else:
            screenbloom.write_config(sat, bri, transition)
            screenbloom.re_initialize()
            print 'Thread is not running!'
    except NameError:
        print 't not defined yet!'
        screenbloom.write_config(sat, bri, transition)
        screenbloom.re_initialize()

    data = {
        'message': 'Updated config file!'
    }

    return jsonify(data)


@app.route('/')
def index():
    config = screenbloom.config_to_list()

    sat = config[3]
    bri = config[4]
    transition = config[5]

    return render_template('/home.html',
                           sat=sat,
                           bri=bri,
                           transition=transition)


@app.route('/new-user')
def new_user():
    return render_template('/new_user.html',
                           title='New User')


@app.route('/start')
def start():
    print 'Firing run function...'

    config = screenbloom.config_to_list()
    trans = config[5]

    global t
    t = ScreenBloomThread(trans)
    t.start()

    print 'Hello!'

    data = {
        'message': 'ScreenBloom thread initialized'
    }

    return jsonify(data)


@app.route('/stop')
def stop():
    print 'Ending screenBloom thread...'

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
        'trans-value': config[5]
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.5')