from .app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(130))
    isadmin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class PageVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ancestor = db.Column(db.Integer, db.ForeignKey('page_version.id'), nullable=True, default=None)
    title = db.Column(db.String(250))
    text = db.Column(db.Text())

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current = db.Column(db.Integer, db.ForeignKey('page_version.id'))