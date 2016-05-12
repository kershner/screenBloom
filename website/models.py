from website import db


class Download(db.Model):
    __bind_key__ = 'sb_db'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    version = db.Column(db.String(64))
    build = db.Column(db.String(64))
