import requests
import pprint
import os
import scraper
from flask import Flask, request


### CONFIGS ###
app = Flask(__name__)
ACCESS_TOKEN = os.environ['FB_ACCESS_TOKEN']

@app.route('/', methods=['POST','GET'])
def main():
 
    challenge = request.args.get("hub.challenge")
    if challenge:
        return challenge

    req = request.get_json(silent=True)

    message = (req['entry'][0]['messaging'][0]['message']['text'])
    message = "Returning Soon"
    uid = (req['entry'][0]['messaging'][0]['sender']['id'])

    print("sending {} to {}".format(message, uid))
    send_message(uid, message)
    return 'OK'

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

