import requests
import json
import redis
import pprint
import os
import scraper
import logging
from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired


logger = logging.getLogger(__name__)

class RegisterForm(FlaskForm):
    regno = StringField('Registration Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    uid = HiddenField('uid')
    submit = SubmitField('Register')

### CONFIGS ###
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
ACCESS_TOKEN = os.environ['FB_ACCESS_TOKEN']

r = redis.Redis(host='localhost', port=6379)

@app.route('/MIT-Hodor', methods=['POST','GET'])
def main():
    try:
        logger.debug('Got request') 
        challenge = request.args.get("hub.challenge")
        if challenge:
            return challenge

        req = request.get_json(silent=True)

        message_recieved = (req['entry'][0]['messaging'][0]['message']['text'])
        uid = (req['entry'][0]['messaging'][0]['sender']['id'])

        if r.exists(uid):
            handle_message(uid, message_recieved)
        else:
            handle_new_user(uid)

    except Exception as e:
        logger.debug(str(e))
    
    return 'OK'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        key = request.args.get('key')
    	if r.exists('IN_REG:'+key):
            form = RegisterForm(uid=key)
            return render_template('register.html', form=form)
   	else:
            return '404'
    else:
        regno = request.form.get('regno')
        password = request.form.get('password')
        uid = request.form.get('uid')
        r.set(uid, json.dumps({'regno' : regno, 'password' : password}))
        return '<h1> Registration complete {}</h1>'.format(str(uid))


def handle_new_user(uid):
    uid_hash = uid ## Change this
    print(uid)
    r.setex('IN_REG:'+uid_hash, 'unregistered', 300)

    register_url = "https://kalbhor.xyz/register?key={}".format(uid_hash)
    send_message(uid, "Register on this url : {}".format(register_url))

def handle_message(uid, message):
    details = r.get(uid)
    details = json.loads(details)
    resp = scraper.main(details['regno'], details['password'])
    send_message(uid, str(resp))

def send_message(uid, message):
    data = {
  	"messaging_type": "RESPONSE",
  	"recipient": {
    	"id": uid
  	},
  	"message": {
    	"text": message
  	}
    }

    return requests.post('https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(ACCESS_TOKEN), json=data)

if __name__ == '__main__':
    app.run(debug=True, port=8000)

