from flask import Flask, render_template, jsonify
import screenbloom
import urllib2
import os
import time

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/')
def index():
    return render_template('/home.html')


@app.route('/new-user')
def new_user():
    return render_template('/new_user.html',
                           title='New User')


@app.route('/start')
def start():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open('%s/config.txt' % current_path, 'r') as config_file:
            config = list(config_file)

    screen = screenbloom.initialize(config)
    while True:
        results = screenbloom.screen_avg()
        try:
            # Update Hue bulbs to avg color of screen
            screenbloom.update_bulb(screen, results['hue_color'], results['screen_hex'])
        except urllib2.URLError:
            print 'Connection timed out, continuing...'
            pass

        print 'HEX: ', results['screen_hex']
        # Wait half a second, repeat
        time.sleep(0.50)

    data = {
        'message': 'ScreenBloom stopped'
    }

    return jsonify(data)


@app.route('/stop')
def stop():
    print 'Firing stop function...'

    data = {
        'message': 'Set session variable to False'
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)