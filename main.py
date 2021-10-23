from flask import Flask, request
import os
import codecs, time
from bot import racer
import threading
import json
import random
from cryptography.fernet import Fernet
import string
from automation import get_cookies
import asyncio
chars = list(string.ascii_letters+string.punctuation+string.digits)
index = chars.index('\'')
del chars[index]
index = chars.index('\"')
del chars[index]
def write_json(data, file='info.json'):
    with open('info.json', 'w') as f:
        json.dump(data, f, indent=4)
key = os.getenv('key')
def encrypt(message):
    """
    Encrypts a message
    """
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return (encrypted_message.decode())
app=Flask(__name__)
@app.route('/', methods=['HEAD', 'GET'])
def main():
    file = codecs.open("main.html", "r", "utf-8")
    return file.read()
@app.route('/start', methods=['POST'])
def start():
    def post():
        request.post('https://sanbox-server-3.joshuatucker3.repl.co/botstart')

    thread = threading.Thread(target=post)
    thread.start()
    thread.join(2)
    return 'startedbot'


@app.route('/startbotting', methods=['POST'])
def startbotting():
    form = request.form
    username = form['username']
    password = form['password']
    print('username:' + request.form['username'])
    print('password:' + request.form['password'])
    speed = int(form['speed'])
    accuracy = int(form['accuracy'])
    global bot
    bot = racer(username, password, speed, accuracy, 100000, 'true')
    thread = threading.Thread(target=bot.startBot())
    thread.start()
    thread.join(3)
    return 'started bot'

@app.route('/accs', methods=['POST'])
def accs():
    form = request.form
    if form['key'] == os.getenv('password'):
        with open('info.json') as f:
            data = json.load(f)
            return data

if __name__ == "__main__":
    app.run(threaded=True, port=5000, host='0.0.0.0')
