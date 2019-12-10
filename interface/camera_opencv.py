import os
import cv2
from base_camera import BaseCamera
from func import contorno2
from values import Values

class Camera(BaseCamera):
    video_source = 0

    def __init__(self, video_source='video_original.avi'):
        # BaseCamera.thread=None
        Camera.set_video_source(video_source)
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        alfa = 5 # alfa é o limiar de angulo para que apareça um contorno
        count = 0
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        cap = cv2.VideoCapture("output.mkv")
        capOriginal = cv2.VideoCapture("original.avi")


        while True:
            ret, teste = cap.read()
            retOriginal, imgOriginal = capOriginal.read()
            # ret, frame = camera.read()
            # _, frame_original = camera.read()
            img = contorno2(ret, teste, retOriginal, imgOriginal)
            # cv2.rectangle(img, (50, 0), (300, 720), (0, 255, 0), 2)

            # TODO adaptar para o novo vídeo
            # ret, frame = camera.read()
            # _, frame_original = camera.read()
            # img, count = contorno2(frame, frame_original, alfa)
            # Values.set_toast_count(count)
            # cv2.rectangle(img, (50, 0), (300, 720), (0, 255, 0), 2)

            # cv2.imshow('frame', img)
            if (cv2.waitKey(30) != -1):  # aperta ESC e a janela fecha
                break
            yield cv2.imencode('.jpg', img)[1].tobytes()
