import cv2
from func import contorno2
cap = cv2.VideoCapture("fundo_preto_torrada_branca.avi")
cap_original = cv2.VideoCapture('video_original.avi')


def show_original_video(alfa):
    while True:
        ret, frame = cap.read()
        _, frame_original = cap_original.read()
        cv2.rectangle(frame_original, (50, 0), (300, 670), (0, 255, 0), 2)
        if (ret):
            frame = contorno2(frame_original, alfa)
            cv2.imshow('frame', frame)
        if (cv2.waitKey(30) != -1):  # aperta ESC e a janela fecha
            break
    cap.release()
    cv2.destroyAllWindows()

show_original_video(5)