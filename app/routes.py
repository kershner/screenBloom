from flask import Flask, render_template, session, jsonify
import screenbloom
import urllib2
import os
import time

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/')
def index():
    session['running'] = False

    return render_template('/home.html')


@app.route('/new-user')
def new_user():
    print session['running']

    return render_template('/new_user.html',
                           title='New User')


def check_session():
    print '\nResult of check_session(): ', session['running']
    return session['running']


@app.route('/start')
def start():
    session['running'] = True
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open('%s/config.txt' % current_path, 'a+') as config_file:
        config = list(config_file)

    screen = screenbloom.initialize(config)
    while session['running']:
        if not check_session():
            session['running'] = False
        else:
            results = screenbloom.screen_avg()
            try:
                screenbloom.update_bulb(screen, results['hue_color'], results['screen_hex'])
            except urllib2.URLError:
                print 'Connection timed out, continuing...'
                pass

            print 'HEX: ', results['screen_hex']
            #print 'HSV: ', results['hsv_color']
            time.sleep(0.50)

    data = {
        'message': 'ScreenBloom stopped'
    }

    return jsonify(data)


@app.route('/stop')
def stop():
    session['running'] = False
    print 'Firing stop function...'
    data = {
        'message': 'Set session variable to False'
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)