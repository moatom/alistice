from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    root_id = Column(Integer, ForeignKey('bookmark.id', ondelete='CASCADE'))
    root = relationship('Bookmark',
                        cascade="all, delete-orphan",
                        single_parent=True,
                        foreign_keys=[root_id],
                        backref=backref('root_s_owner',
                                        cascade="all, delete-orphan",
                                        passive_deletes=True,
                                        uselist=False)
                        )

    def __init__(self, root):
        self.root = root

    def __repr__(self):
        return "User(id=%r, root_id=%r)" % (
            self.id,
            self.root_id,
        )

# 本当にrelatiomalな必要ある要素かどうか？

class Bookmark(Base):
    __tablename__ = 'bookmark'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('bookmark.id', ondelete='CASCADE'))
    children = relationship("Bookmark",
                            cascade="all, delete-orphan",
                            passive_deletes=True,
                            backref=backref("parent", remote_side=id))
    owner_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    owner = relationship('User', foreign_keys=[owner_id])

    def __init__(self, type, parent, owner):
        self.type = 0
        self.parent = parent
        self.owner = owner

    def __repr__(self):
        return "Bookmark(id=%r, parent_id=%r, owner_id=%r)" % (
            self.id,
            self.parent_id,
            self.owner_id)


from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


if __name__ == "__main__":
    import os
    engine = create_engine("sqlite://" + os.path.dirname(__file__) + '/test.db', echo=True)
    Base.metadata.create_all(engine)
    session = Session(engine)

    print('===================insert')
    root = Bookmark(0, None, None)
    owner = User(root)
    session.add(owner)
    session.commit()

    root.owner = owner
    session.commit()

    node = Bookmark(0, root, owner)
    node2 = Bookmark(0, root, owner)
    node3 = Bookmark(0, node2, owner)
    node4 = Bookmark(0, node3, owner)
    session.add(node)
    session.commit()
    
    print(owner)
    print(session.query(User).all())
    print(session.query(Bookmark).all())

    session.expire_all()


    print('===================delete')
    # session.delete(owner)
    session.commit()
    session.query(User).filter(User.root!=None).delete() # all
    # session.query(Bookmark).filter(Bookmark.parent==None).delete() # all
    # session.query(Bookmark).filter(Bookmark.parent!=None).delete() # leaf
    print(session.query(User).all())
    print(session.query(Bookmark).all())
    session.commit()



    # root = Bookmark(**{'type': 0,
    #                    'title': 'root'})
    # user = User(**user_a, root=root)
    # db.session.add(user)
    # db.session.commit()

    # root.owner = user
    # db.session.commit()

    # db.session.query(User).filter(id=current_user.id).delete()
    # db.session.commit()
    # db.session.delete(current_user)
    #     db.session.commit()