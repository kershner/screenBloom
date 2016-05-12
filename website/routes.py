from flask import Flask, render_template, request
from datetime import datetime
from website import models, db
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def screenbloom():
    return render_template('/welcome.html')


@app.route('/download-analytics', methods=['POST'])
def download_analytics():
    if request.method == 'POST':
        build = request.json
        new_download = models.Download(date=datetime.now(), version='1.6', build=build)
        db.session.add(new_download)
        db.session.commit()
        return 'Hello world!'


if __name__ == '__main__':
    app.run(debug=True)
