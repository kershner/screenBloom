from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def screenbloom():
    return render_template('/welcome.html')


@app.route('/download-analytics', methods=['POST'])
def download_analytics():
    if request.method == 'POST':
        # Eventually save some info to a DB?
        # data = request.json

        print '####################################'
        print 'Someone is downloading ScreenBloom!'

        return 'Hello world!'


if __name__ == '__main__':
    app.run(debug=True)
