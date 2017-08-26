import os
import scraper.slcm as scraper
import parser.parser as parser
import parser.responses as responses
import parser.dbase as database
import requests
import fbmq
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from wit import Wit


### CONFIGS ###
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
page = fbmq.Page(os.environ["PAGE_ACCESS_TOKEN"])
wit_client = Wit(os.environ["WIT_TOKEN"])
dbase = database.handler(db)
responder = responses.messages()

quick_replies = [
        fbmq.QuickReply(title="What can you do?", payload="WHAT"),
        fbmq.QuickReply(title="Attendance", payload="ATTENDANCE"),
        fbmq.QuickReply(title="Timetable", payload="TIMETABLE"),
        fbmq.QuickReply(title="Teacher Guardian", payload="TEACHER"),
    ]

### DB Skeleton ###
class User(db.Model):
    fbid = db.Column(db.String(80), primary_key=True)
    rollno = db.Column(db.String(80), unique=True, nullable=True)
    password = db.Column(db.String(80), nullable=True)
    group = db.Column(db.String(80), nullable=True)
    name = db.Column(db.String(80), nullable=True)

    def __init__(self, fbid, rollno=None, password=None, group=None, name=None):
        self.fbid = fbid
        self.rollno = rollno
        self.password = password
        self.group = group
        self.name = name

    def __repr__(self):
        return '< <Name>{} <Rollno>{} >'.format(self.name, self.rollno)

@page.handle_delivery
def delivery_handler(payload):
    print("Message delivered")

@page.handle_echo
def echo_handler(payload):
    print('Message echoed')

@page.handle_postback
def postback_handler(payload):
    print('postback pressed')

@page.after_send
def after_send(payload, response):
    print("Done")

@page.handle_read
def read_hanlder(payload):
    print("Message read by user")


### Handles Fb verification ###
@app.route('/', methods=['POST'])
def webhook():
    page.handle_webhook(request.get_data(as_text=True))
    return "ok"

### Main method (Handles user messages, db) ###
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
        page.send(sender_id, responder.menu)
        page.send(sender_id, responder.new_user)
    else:
        user = User.query.filter_by(fbid = sender_id).first()
        if user.name is None:
            user_profile = page.get_user_profile(sender_id)
            print(user_profile)
            try:
                user.name = "{} {}".format(user_profile['first_name'], user_profile['last_name'])
                db.session.commit()
            except KeyError:
                if 'name' in user_profile:
                    user.name = "{}".format(user_profile['name'])
                    db.session.commit()
                else:
                    pass

        if user.group is None and user.rollno is not None and user.password is not None:
            try:
                driver = scraper.login(user.rollno, user.password)
            except:
                driver = None
            if driver is not None:
                group = scraper.group(driver)
                user.group = group
                db.session.commit()
                scraper.end(driver)

        if user.rollno  == None:
            ### User has entered regno ###
            dbase.regno(message, user)
            page.send(sender_id, responder.new_user_pass)
        elif user.password == None:
            ### User has entered password ###
            dbase.password(message, user)

            if scraper.login(user.rollno, user.password) is None:
                    ### Remove record if wrong details have been entered ###
                    ### Goes back to step 1 (Enter regno) ###
                    dbase.delete(user)
                    page.send(sender_id, responder.wrong)
            else:
                    driver = scraper.login(user.rollno, user.password)
                    group = scraper.group(driver)
                    dbase.group(group, user)
                    page.send(sender_id, responder.verified)
                    scraper.end(driver)

        else:
            user = User.query.filter_by(fbid = sender_id).first()

            page.typing_on(sender_id)
            resp = parser.witintent(message, wit_client)

            try:
                driver = scraper.login(user.rollno, user.password)
            except:
                driver = None
                resp = {}
            print(resp)
            if resp != {}:
                if driver is None:
                    dbase.delete(user)
            else:
                page.send(sender_id, "Hodor!")
            ### Parsing responses begins here ###

            if 'greetings' in resp:
                page.send(sender_id, 'Hello hello!')

            if 'thanks' in resp:
                page.send(sender_id, "You're welcome!")

            if 'guardian' in resp:
                guardian_data = scraper.guardian(driver)
                response, phone = parser.guardian(resp, guardian_data)
                page.send(sender_id, str(response))
                if phone != None:
                    page.send(sender_id, fbmq.Template.Buttons("Smart response", [fbmq.Template.ButtonPhoneNumber("Call now", phone)]))

            if 'timetable' in resp:
                timetable_data = scraper.timetable(driver)
                response = parser.timetable(resp, timetable_data)
                page.send(sender_id, str(response))

            if 'attendance' in resp or 'subject' in resp:
                group = user.group
                attendance_data = scraper.attendance(driver)
                response = parser.attendance(resp, attendance_data, group)
                print(str(response))
                for resp in response:
                    try:
                        page.send(sender_id, str(resp))
                    except ValueError:
                        print('Faced value error {}'.format(resp))

            if 'curse' in resp:
                page.send(sender_id, responder.curse)

            if 'hodor' in resp:
                page.send(sender_id, "HODOOOOOR!")

            if 'showoff' in resp:
                page.send(sender_id,responder.menu)
                page.send(sender_id, "Check out this video : {}".format(responder.video))
    
            scraper.end(driver)
            page.send(sender_id, "*Quick Menu*", quick_replies=quick_replies,
            metadata="DEVELOPER_DEFINED_METADATA")


if __name__ == '__main__':
    app.run(debug=True)
