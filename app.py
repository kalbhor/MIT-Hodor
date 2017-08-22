import os
import scraper.slcm as scraper
import parser.parser as parser
import parser.dbase as database
import requests
import fbmq
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from wit import Wit


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
page = fbmq.Page(os.environ["PAGE_ACCESS_TOKEN"])
wit_client = Wit(os.environ["WIT_TOKEN"])

dbase = database.handler(db)


class User(db.Model):
    fbid = db.Column(db.String(80), primary_key=True)
    rollno = db.Column(db.String(80), unique=True, nullable=True)
    password = db.Column(db.String(80), nullable=True)

    def __init__(self, fbid, rollno=None, password=None):
        self.fbid = fbid
        self.rollno = rollno
        self.password = password

    def __repr__(self):
        return '<Rollno> %r>' % self.rollno

@app.route('/', methods=['POST'])
def webhook():
    page.handle_webhook(request.get_data(as_text=True))
    return "ok"

@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    ### get user sending request ###
    client = User.query.filter_by(fbid=sender_id).first()

    if client is None:
        ### User doesn't exist on DB ###
        user = User(sender_id)
        dbase.new_user(sender_id, user)
        page.send(sender_id, "I can't recognise you.")
        page.send(sender_id, "Enter your SLCM registration number")
    else:
        user = User.query.filter_by(fbid = sender_id).first()
        if user.rollno  == None:
            ### User has entered regno ###
            dbase.regno(message, user)
            page.send(sender_id, "Enter your SLCM password (Don't worry, we can't see your password)")
        elif user.password == None:
            ### User has entered password ###
            dbase.password(message, user)

            if scraper.login(user.rollno, user.password) is None:
                    ### Remove record if wrong details have been entered ###
                    ### Goes back to step 1 (Enter regno) ###
                    dbase.delete(user)
                    page.send(sender_id, "Wrong details")
            else:
                    page.send(sender_id, "Successfully verified. \nYou may now begin chatting")

        else:
            user = User.query.filter_by(fbid = sender_id).first()

            page.typing_on(sender_id)
            resp = parser.witintent(message, wit_client)
            if resp != {}:
                driver = scraper.login(user.rollno, user.password)
                if driver is None:
                    dbase.delete(user)
            else:
                page.send(sender_id, "Couldn't analyse that.\n Ask me something like : 'What's my attendance in PSUC'\n'Can I bunk maths?'\n 'What's tomorrow's timetable'\netc etc")

            ### Parsing responses begins here ###

            if 'hello' in resp:
                page.send(sender_id, 'Hello hello')

            if 'guardian' in resp:
                guardian_data = scraper.guardian(driver)
                response = parser.guardian(resp, guardian_data)
                page.send(sender_id, str(response))

            if 'timetable' in resp:
                timetable_data = scraper.timetable(driver)
                response = parser.timetable(resp, timetable_data)
                page.send(sender_id, str(response))

            if 'attendance' in resp:
                attendance_data = scraper.attendance(driver)
                response = parser.attendance(resp, attendance_data)
                page.send(sender_id, str(response))

            if 'curse' in resp:
                page.send(sender_id, "Tera baap!")


@page.after_send
def after_send(payload, response):
    print("Done")


if __name__ == '__main__':
    app.run(debug=True)
