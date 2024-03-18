from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Users database
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    phone_number = db.Column(db.String, unique=True)
    address = db.Column(db.String)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)
    dob = db.Column(db.String)
    bio = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    friendships = db.relationship('Friendship', back_populates='user', foreign_keys='Friendship.user_id')

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"
    
# Frienships database
class Friendship(db.Model):
    __tablename__ = 'friendships'

    friendship_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    friend_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    friend_request = db.Column(db.Boolean, default=True)
    chat = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='friendships', foreign_keys=[user_id])
    friend = db.relationship('User', back_populates='friendships', foreign_keys=[friend_id])

    def __repr__(self):
        return f"<User user_id={self.user_id} Friend friend_id={self.friend_id}>"
    
# Activity database
class Activity(db.Model):
    __tablename__ = 'activity'

    activity_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete='CASCADE'))
    activity_name = db.Column(db.String)

    user = db.relationship("User", backref=db.backref("activities", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Activity activity_id={self.activity_id} activity_name={self.activity_name}>"
    
# Message database 
class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    content = db.Column(db.String)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def __repr__(self):
        return f"<Message message_id={self.message_id} sender_id={self.sender_id} receiver_id={self.receiver_id}>"

# Database connection
def connect_to_db(flask_app, db_uri="postgresql://owenclary:Goodmom58@localhost:5432/trail_twin", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
