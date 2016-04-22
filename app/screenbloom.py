from flask import Flask, render_template, jsonify, request
from modules import screenbloom_functions as sb
import jinja2.ext
import threading
import socket
import os

app = Flask(__name__)  # Development
# app = Flask(__name__, static_url_path='', static_folder='', template_folder='')  # Production
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    global startup_thread
    if startup_thread.is_alive():
        startup_thread.join()

    data = sb.get_index_data()
    return render_template('/home.html',
                           update=data['update'],
                           min_bri=data['min_bri'],
                           default=data['default'],
                           default_color=data['default_color'],
                           lights=data['lights'],
                           expanded_lights=data['expanded_lights'],
                           lights_number=data['lights_number'],
                           icon_size=data['icon_size'],
                           username=data['username'],
                           party_mode=data['party_mode'],
                           title='Home')


@app.route('/start')
def start():
    data = sb.start_screenbloom()
    return jsonify(data)


@app.route('/stop')
def stop():
    data = sb.stop_screenbloom()
    return jsonify(data)


@app.route('/new-user')
def new_user():
    return render_template('/new_user.html',
                           title='New User')


@app.route('/manual')
def manual():
    return render_template('/new_user_manual.html',
                           title='Manual IP')


@app.route('/register', methods=['GET', 'POST'])
def register():
    username = request.args.get('username', 0, type=str)
    hue_ip = request.args.get('hue_ip', 0, type=str)
    data = sb.register_logic(username, hue_ip, local_host)
    return jsonify(data)


@app.route('/update-config')
def update_config():

    active_bulbs = request.args.get('bulbs', 0, type=str)
    update = request.args.get('update', 0, type=str)
    bri = request.args.get('bri', 0, type=str)
    min_bri = request.args.get('minBri', 0, type=str)
    helper = sb.rgb_cie.ColorHelper()
    default = helper.hexToRGB(request.args.get('defaultColor', 0, type=str))
    default = '%d,%d,%d' % (default[0], default[1], default[2])
    party_mode = request.args.get('partyMode', 0, type=str)

    data = sb.update_config_logic(bri, active_bulbs, update, default, min_bri, party_mode)
    return jsonify(data)


@app.route('/get-settings')
def get_settings():
    data = sb.get_settings_logic()

    return jsonify(data)


@app.route('/on-off')
def on_off():
    state = request.args.get('state', 0, type=str)
    sb.lights_on_off(state)
    data = {
        'message': 'Turned lights %s' % state
    }
    return jsonify(data)


@app.route('/beta')
def beta():
    return render_template('/beta.html',
                           title='Home')

if __name__ == '__main__':
    local_host = socket.gethostbyname(socket.gethostname())
    startup_thread = sb.StartupThread(local_host)
    startup_thread.start()
    app.run(debug=True, host=local_host, use_reloader=False)
