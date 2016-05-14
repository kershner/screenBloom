from flask import Flask, render_template, request, session, abort
from datetime import datetime
from website import models, db
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            abort(401)
    return wrap


@app.route('/')
def screenbloom():
    return render_template('/welcome.html')


@app.route('/download-analytics', methods=['POST'])
def download_analytics():
    if request.method == 'POST':
        data = request.json
        build = data['build']
        version = data['version']
        new_download = models.Download(date=datetime.now(), version=version, build=build)
        db.session.add(new_download)
        db.session.commit()
        return 'Hello world!'


if __name__ == '__main__':
    app.run(debug=True)
