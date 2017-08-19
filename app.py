import os
import scraper.slcm as scraper

import requests
import fbmq
from flask import Flask, request
from wit import Wit

from flask_sqlalchemy import SQLAlchemy

from datetime import date
import calendar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
page = fbmq.Page(os.environ["PAGE_ACCESS_TOKEN"])
client = Wit(os.environ["WIT_TOKEN"])


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

def intent(msg):
    resp = client.message(msg)
    return resp['entities']

def guardian_resp(values, data):
    values = values['guardian']
    resp = ""

    response = { 
            'guardian' : "Your teacher guardian is {}. ".format(data['name']), 
            'number' : "Phone number - {}. ".format(data['phone']), 
            'mail' : "email ID: {}. ".format(data['email'])
            }

    for val in values:
        resp += response[val['value']]

    return resp


def timetable_resp(values, data):
    today = calendar.day_name[date.today().weekday()].lower()
    tomorrow = calendar.day_name[date.today().weekday()+1].lower()



    # timetable = values['timetable']
    time = values['time'][0]['value']
    if time == 'today':
        time = today
    elif time == 'tomorrow':
        time = tomorrow

    response = "The timetable for {} is : \n\n ".format(time.upper())

    for subj in data[time]:
        t, sub = subj
        response += "({}) - {} \n\n".format(t,sub)

    return response



    




@app.route('/', methods=['POST'])
def webhook():
    page.handle_webhook(request.get_data(as_text=True))
    return "ok"

@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    # User sending request
    client = User.query.filter_by(fbid=sender_id).first()

    if client is None: # User doesn't exist on DB
        new_user = User(sender_id)
        db.session.add(new_user)
        db.session.commit()
        page.send(sender_id, "I can't recognise you.")
        page.send(sender_id, "Enter your registration number")
    else:
        ex_user = User.query.filter_by(fbid = sender_id).first()
        if ex_user.rollno  == None:
            ex_user.rollno = message
            db.session.add(ex_user)
            db.session.commit()
            page.send(sender_id, "Enter password")
        elif ex_user.password == None:
            ex_user.password = message
            db.session.add(ex_user)
            db.session.commit()
            if scraper.login(ex_user.rollno, ex_user.password) is None:
                db.session.delete(ex_user)
                db.session.commit()
                page.send(sender_id, "Wrong details")
            else:
                page.send(sender_id, "Succesfully logged in")

        else:
            fi_user = User.query.filter_by(fbid = sender_id).first()

            page.typing_on(sender_id)
            resp = intent(message)
            if resp != {}:
                driver = scraper.login(fi_user.rollno, fi_user.password)
            else:
                page.send(sender_id, "I couldn't analyse that")

            #timetable = scraper.timetable(driver)

            if 'guardian' in resp:
                guardian_data = scraper.guardian(driver)
                response = guardian_resp(resp, guardian_data)
                page.send(sender_id, str(response))

            if 'timetable' in resp:
                timetable_data = scraper.timetable(driver)
                response = timetable_resp(resp, timetable_data)
                page.send(sender_id, str(response))

            page.send(sender_id, str(resp))


@page.after_send
def after_send(payload, response):
    print("Done")


if __name__ == '__main__':
    app.run(debug=True)
