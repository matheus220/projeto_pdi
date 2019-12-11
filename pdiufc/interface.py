import os
import cv2
import json
import asyncio
import logging
import threading
import websockets

from flask import Response
from flask import Flask
from flask import render_template

logging.basicConfig()

image_not_found = cv2.imread(os.path.join("pdiufc", "static", "img", "image-not-found.png"))
output_frame = image_not_found
lock = threading.Lock()
app = Flask(__name__)

STATE = {
    'count_tor_tot': 0,
    'count_tor_alvo': 0,
    'count_tor_alvo_tela': 0,
    'velocity': 0,
    'input_video': ['webcam']
}

USERS = set()


def process(processed_data, original_image):
    global output_frame
    STATE['count_tor_tot'] = processed_data['count_tor_tot']
    STATE['count_tor_alvo'] = processed_data['count_tor_alvo']
    STATE['count_tor_alvo_tela'] = processed_data['count_tor_alvo_tela']

    for t in processed_data['tor_alvo']:
        cm = (int(t[0]), int(t[1]))
        cv2.circle(original_image, cm, 10, (0, 0, 255), -1)
        cv2.putText(original_image, str(t[2]), (cm[0]-20, cm[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.rectangle(original_image, (cm[0]-20, cm[1]-20), (cm[0]+20, cm[1]+20), (0, 255, 200), 2)

    cv2.line(original_image, (100, 0), (100, 720), (0, 255, 0), 2)
    cv2.line(original_image, (250, 0), (250, 720), (0, 255, 0), 2)
    # cv2.imshow('output', original_image)
    # cv2.waitKey(1)
    with lock:
        output_frame = original_image.copy()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notify_state)
    loop.close()


# ###################### WEBSOCKET ######################


def state_event():
    return json.dumps({"type": "state", **STATE})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)


async def unregister(websocket):
    USERS.remove(websocket)


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "minus":
                STATE["value"] -= 1
                await notify_state()
            elif data["action"] == "plus":
                STATE["value"] += 1
                await notify_state()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)


# ##################### WEB SERVER ######################


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
            threaded=True, use_reloader=False)
