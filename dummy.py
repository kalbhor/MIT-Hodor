import requests
import json
import os
import logging
from flask import Flask, request, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
ACCESS_TOKEN = os.environ['FB_ACCESS_TOKEN']

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

    send_message(uid, 'Coming back, soon')
    return 'OK'

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

