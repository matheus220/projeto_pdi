import os
import cv2
import threading
from flask import Response
from flask import Flask
from flask import render_template

image_not_found = cv2.imread(os.path.join("pdiufc", "static", "img", "image-not-found.png"))

output_frame = image_not_found
lock = threading.Lock()
app = Flask(__name__)


def process(processed_data, original_image):
    global output_frame
    print(processed_data['count_tor_tot'])
    print(processed_data['count_tor_alvo'])
    print(processed_data['count_tor_alvo_tela'])
    for t in processed_data['tor_alvo']:
        cv2.circle(original_image, (int(t[0]), int(t[1])), 30, (0, 0, 255), -1)
    # cv2.imshow('output', original_image)
    # cv2.waitKey(1)
    with lock:
        output_frame = original_image.copy()


def generate():
    # grab global references to the output frame and lock variables
    global output_frame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output_frame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def launch_web_server():
    app.run(host='0.0.0.0', port=80, debug=False,
            threaded=False, use_reloader=False)
