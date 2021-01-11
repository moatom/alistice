from src.extentions import db
from datetime import datetime


class Bookmark(db.Model):
    __tablename__ = 'bookmark'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)# 0:folder, 1:bookmark
    title = db.Column(db.String(100), nullable=False, default='<empty>')# / is bad char?
    url = db.Column(db.String(2048))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('bookmark.id', ondelete='CASCADE'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    children = db.relationship(
        "Bookmark",
        cascade="all, delete-orphan",
        passive_deletes=True,
        backref=db.backref("parent", remote_side=id),
    )
    owner = db.relationship('User', foreign_keys=[owner_id])

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Bookmark({title!r})>'.format(title=self.title)