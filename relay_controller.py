#!/usr/bin/python
# -*- coding:UTF-8 -*-

from flask import Flask, request, send_from_directory
import RPi.GPIO as GPIO
import socket
import os

app = Flask(__name__, static_folder='.')

# GPIO Pin config
Relay = [26, 20, 21, 16]
Relay_status = [1, 1, 1, 1]

GPIO.setmode(GPIO.BCM)
for pin in Relay:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/Relay', methods=['POST'])
def relay_control():
    global Relay_status
    for i in range(4):
        val = request.form.get(f'Relay{i+1}')
        if val is not None:
            Relay_status[i] = int(val)
            GPIO.output(Relay[i], Relay_status[i])
    return "OK"

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    localhost = s.getsockname()[0]
    s.close()

    app.run(host=localhost, port=8000)
