from .app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(130))
    isadmin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class PageVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250))
    text = db.Column(db.Text())
    ancestor_id = db.Column(None, db.ForeignKey('page_version.id'), nullable=True, default=None)
    page_id = db.Column(None, db.ForeignKey('page.id'), nullable=False)

    ancestor = db.relationship("PageVersion", foreign_keys=[ancestor_id], uselist=False)
    page = db.relationship("Page", foreign_keys="PageVersion.page_id", backref="versions", uselist=False)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    current_id = db.Column(None, db.ForeignKey('page_version.id'))

    current = db.relationship("PageVersion", foreign_keys="Page.current_id", uselist=False, post_update=True)
