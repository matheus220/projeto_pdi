#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, jsonify
from values import Values

# import camera driver
# if os.environ.get('CAMERA'):
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
#     from camera import Camera
from camera_opencv import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/toastquantity', methods = ['GET'])
def quantity():
    toastcount = str(Values.get_toast_count())
    return jsonify(result=toastcount)


@app.route('/speed', methods = ['GET'])
def speed():
    spd = str(Values.get_speed())
    return jsonify(result=spd)


def gen(camera):
    """Video streaming generator function.""" 

    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<int:source_num>')
def video_feed(source_num):
    if source_num == 1:
        video_source = 'video_original.avi'
    elif source_num == 2:
        video_source = 'fundo_preto_torrada_branca.avi'

    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(video_source='video_original.avi')),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
