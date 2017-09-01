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

    def group(self, group, user):
        user.group = group
        self.db.session.add(user)
        self.db.session.commit()

    def delete(self, user):
        self.db.session.delete(user)
        self.db.session.commit()

    def name(self, name, user):
        user.name = name
        db.session.commit()

    def semester(self, sem, user):
        user.semester = sem
        db.session.commit()


