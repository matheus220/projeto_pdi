import asyncio
import os
import cv2
from queue import Queue
from threading import Thread

import websockets

from pdiufc import processing, preprocessing, interface

raw_frame_queue = Queue()
original_frame_queue = Queue()
preprocessed_frame_queue = Queue()
processed_data_queue = Queue()


def process_data(processing_function, input_queue, output_queue, auxiliary_queue=None):
    while True:
        input_data = input_queue.get()

        if auxiliary_queue:
            auxiliary_input = auxiliary_queue.get()
            if output_queue:
                output_data = processing_function(input_data, auxiliary_input)
                output_queue.put(output_data)
            else:
                processing_function(input_data, auxiliary_input)
        else:
            if output_queue:
                output_data = processing_function(input_data)
                output_queue.put(output_data)
            else:
                processing_function(input_data)

        input_queue.task_done()


web_server_thread = Thread(target=interface.launch_web_server)
web_server_thread.setDaemon(True)
web_server_thread.start()

pre_processing_thread = Thread(target=process_data, args=(preprocessing.process, raw_frame_queue, preprocessed_frame_queue))
pre_processing_thread.setDaemon(True)
pre_processing_thread.start()

processing_thread = Thread(target=process_data, args=(processing.process, preprocessed_frame_queue, processed_data_queue))
processing_thread.setDaemon(True)
processing_thread.start()

interface_thread = Thread(target=process_data, args=(interface.process, processed_data_queue, None, original_frame_queue))
interface_thread.setDaemon(True)
interface_thread.start()

videos = ["webcam"]

for file in os.listdir("results"):
    if file.endswith(".avi"):
        videos.append(file.split('.')[0])

interface.STATE['input_video'] = videos


def video_player():
    while True:
        with interface.lock_state:
            active = interface.STATE['active']
            source_name = interface.STATE['video_src']

        if not active:
            cv2.waitKey(15)
            continue
        elif source_name:
            source_name = os.path.join("results", source_name + '.avi')
            input_video = cv2.VideoCapture(source_name)

            while(input_video.isOpened()):
                with interface.lock_state:
                    if not interface.STATE['active']:
                        break

                ret, frame = input_video.read()

                if ret:
                    roi = frame[:, 100:250:1]
                    raw_frame_queue.put(roi)
                    original_frame_queue.put(frame)
                else:
                    with interface.lock_state:
                        interface.STATE['active'] = False
                        interface.STATE['video_src'] = ''
                    break

                if cv2.waitKey(33) & 0xFF == ord('q'):
                    with interface.lock_state:
                        interface.STATE['active'] = False
                        interface.STATE['video_src'] = ''
                    break

            input_video.release()


video_player_thread = Thread(target=video_player)
video_player_thread.setDaemon(True)
video_player_thread.start()

start_server = websockets.serve(interface.counter, "127.0.0.1", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
