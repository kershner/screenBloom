from flask import Flask, render_template, jsonify
from screen_avg import screen_avg

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('/home.html')


@app.route('/get-screen-color')
def get_screen_color():
    colors = screen_avg()
    print colors

    data = {
        'screen_hex': colors['screen_hex']
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)