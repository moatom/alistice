from src.extentions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt


# https://help.twitter.com/en/managing-your-account/twitter-username-rules
# https://office-hack.com/gmail/password/
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    username = db.Column(db.String(15), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False, default="Anonymous")
    password = db.Column(db.String(128), nullable=False)
    root_id = db.Column(db.String(24))
    # root_id = db.Column(db.Integer, db.ForeignKey('bookmark.id', ondelete='CASCADE'))
    # https://stackoverflow.com/questions/414952/sqlalchemy-datetime-timezone
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    # updated_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    # bio = Column(db.String(300), nullable=True)
    # root = db.relationship('Bookmark',
    #                     cascade="all, delete-orphan",
    #                     single_parent=True,
    #                     foreign_keys=[root_id],
    #                     backref=db.backref('root_s_owner',
    #                                     cascade="all, delete-orphan",
    #                                     passive_deletes=True,
    #                                     uselist=False)
    #                     )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({!r})>'.format(self.username)
        