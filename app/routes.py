from flask import Flask, render_template, jsonify, request
import screenbloom
import os

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/update-config')
def update_config():
    sat = request.args.get('sat', 0, type=str)
    bri = request.args.get('bri', 0, type=str)
    transition = request.args.get('transition', 0, type=str)

    current_path = os.path.dirname(os.path.abspath(__file__))
    with open('%s/config.txt' % current_path, 'r') as config_file:
        config = '\n'.join(config_file).split()

    with open('%s/config.txt' % current_path, 'w+') as config_file:
        config_file.write(config[0] + '\n')
        config_file.write(config[1] + '\n')
        config_file.write(config[2] + '\n')
        config_file.write(sat + '\n')
        config_file.write(bri + '\n')
        config_file.write(transition + '\n')
        config_file.write(config[6] + '\n')
    data = {
        'message': 'Updated config file!'
    }

    return jsonify(data)


@app.route('/')
def index():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open('%s/config.txt' % current_path, 'r') as config_file:
        config = '\n'.join(config_file).split()
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
    screenbloom.run()
    print 'Hello!'
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