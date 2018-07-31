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

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
ACCESS_TOKEN = os.environ['FB_ACCESS_TOKEN']

r = redis.Redis(host='localhost', port=6379)


class RegisterForm(FlaskForm):
    regno = StringField('Registration Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    uid = HiddenField('uid')
    submit = SubmitField('Register')

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route('/MIT-Hodor', methods=['POST','GET'])
def main():
    challenge = request.args.get("hub.challenge")
    if challenge:
        app.logger.info('Recieved webhook verification (hub.challenge)')
        return challenge

    req = request.get_json(silent=True)
    uid = (req['entry'][0]['messaging'][0]['sender']['id'])

    try:
    	message_recieved = (req['entry'][0]['messaging'][0]['message']['text'])
    except Exception as e:
        app.logger.error('Exception {} faced when recieved {} from uid:{}'.format(str(e), req, uid))
        ## handle_exception(uid, message_recieved)
        send_message(uid, 'Your request faced some error')
        return 'OK'

    if r.exists(uid):
        app.logger.info('Handling message uid:{}, message:{}'.format(uid, message_recieved))
        handle_message(uid, message_recieved)
    else:
        app.logger.info('Handling new user uid:{}'.format(uid))
        handle_new_user(uid)

    return 'OK'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        key = request.args.get('key')
        app.logger.info('uid:{} requested registration'.format(key))
    	if r.exists('IN_REG:'+key):
            app.logger.info('uid:{} is undergoing registration'.format(key))
            form = RegisterForm(uid=key)
            return render_template('register.html', form=form)
   	else:
            app.logger.info('uid:{} expired/invalid registration key'.format(key))
            return '404'
    else:
        regno = request.form.get('regno')
        password = request.form.get('password')
        uid = request.form.get('uid')
        if scraper.login(regno, password) is None:
            app.logger.info('uid:{} provided wrong credentials'.format(uid))
            return '<h1> Wrong credentials </h1>'

        app.logger.info('uid:{} has registered'.format(uid))
        r.delete('IN_REG:'+uid)
        r.set(uid, json.dumps({'regno' : regno, 'password' : password}))
        return '<h1> Registration complete </h1>'


def handle_new_user(uid):
    uid_hash = uid ## Change this

    app.logger.info('setting in_reg for uid:{}'.format(uid_hash))
    r.setex('IN_REG:'+uid_hash, 'unregistered', 300)

    register_url = "https://kalbhor.xyz/register?key={}".format(uid_hash)
    send_message(uid, "Register on this url : {}".format(register_url))

def handle_message(uid, message):
    cache = r.get('CACHE:'+uid)
    if cache is not None:
        app.logger.info('cache hit for uid:{}'.format(uid))
        send_message(uid, 'Cache Hit' + str(cache))
    else:
        details = r.get(uid)
        details = json.loads(details)
        app.logger.info('scraping for uid:{}'.format(uid))
        resp = scraper.main(details['regno'], details['password'])
        app.logger.info('setting cache for uid:{}'.format(uid))
        r.setex('CACHE:'+uid, json.dumps(resp), 600)

        send_message(uid, 'Ran Scraper' + str(resp))

def send_message(uid, message):
    app.logger.info('sending {} to uid:{}'.format(message, uid))
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

