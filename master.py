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
'''
while True:
    print("\n### Available video sources ###")
    for i in range(len(videos)):
        print(str(i+1) + " - " + videos[i])
    print("###############################")
    choice = input('\n-> Choose a video source: ')

    try:
        index = int(choice)-1
        if index < 0:
            raise Exception()

        if index == 0:
            source_name = 0
        else:
            source_name = 'results/' + videos[index] + '.avi'
    except Exception as e:
        print("=> Invalid option <=\n")
        continue

    input_video = cv2.VideoCapture(source_name)
    cv2.namedWindow('output', cv2.WINDOW_AUTOSIZE)

    while(input_video.isOpened()):
        ret, frame = input_video.read()

        if ret:
            roi = frame[:, 100:250:1]
            raw_frame_queue.put(roi)
            original_frame_queue.put(frame)
        else:
            break

        if cv2.waitKey(33) & 0xFF == ord('q'):
            break

    input_video.release()
    cv2.destroyAllWindows()
'''
start_server = websockets.serve(interface.counter, "127.0.0.1", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
