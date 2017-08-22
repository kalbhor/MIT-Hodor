from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

class handler:

    def __init__(self, db):
        self.db = db

    def new_user(self, sender_id, user):
        self.db.session.add(user)
        self.db.session.commit()

    def regno(self, message, user):
        user.rollno = message
        self.db.session.add(user)
        self.db.session.commit()

    def password(self, message, user):
        user.password = message
        self.db.session.add(user)
        self.db.session.commit()

    def delete(self, user):
        self.db.session.delete(user)
        self.db.session.commit()
