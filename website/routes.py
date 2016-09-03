from flask import Flask, render_template, request, jsonify
from flask.ext.cors import cross_origin
from screenbloom import models, db
from datetime import datetime
from sqlalchemy import desc
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def screenbloom():
    current_version = '2.0'
    return render_template('/welcome.html',
                            version=current_version)


@app.route('/version-check', methods=['POST', 'OPTIONS'])
@cross_origin(headers='Content-Type')
def version_check():
    if request.method == 'POST':
        current_version = 2.0
        app_version = float(request.json)

        message = ''
        if app_version < current_version:
            message = 'A new version is available!'

        data = {
            'message': message
        }
        return jsonify(data)
    else:
        return 'You got it, dude'


@app.route('/view-download-analytics')
def view_download_analytics():
    return render_template('/analytics.html')


@app.route('/get-analytics-data', methods=['POST'])
def get_analytics_data():
    if request.method == 'POST':
        dates = request.json
        date1 = datetime.strptime(dates['date1'], '%Y-%m-%d')
        date2 = datetime.strptime(dates['date2'], '%Y-%m-%d')

        Download = models.Download
        downloads = Download.query.filter(Download.date.between(date1, date2)).order_by(desc(Download.id)).all()
        new_downloads = []
        for download in downloads:
            tmp = {
                'id': download.id,
                'date': download.date,
                'version': download.version,
                'build': download.build,
                'location_info': download.location_info,
                'user_agent': download.user_agent
            }
            new_downloads.append(tmp)

        response = {
            'downloads': new_downloads
        }

        return jsonify(response)


# Record download in DB
@app.route('/download-analytics', methods=['POST'])
def download_analytics():
    if request.method == 'POST':
        data = request.json
        build = data['build']
        version = data['version']
        user_agent = str(request.headers.get('User-Agent'))

        try:
            location_info = json.dumps(data['locationInfo'])
        except KeyError:
            location_info = ''

        new_download = models.Download(date=datetime.now(),
                                       version=version,
                                       build=build,
                                       user_agent=user_agent,
                                       location_info=location_info)
        db.session.add(new_download)
        db.session.commit()
        return 'Hello world!'