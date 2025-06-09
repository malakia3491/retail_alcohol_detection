import cv2

# Замените на свой RTSP-поток
rtsp_url = "rtsp://192.168.205.127:8554/h264.sdp"

import cv2

print(cv2.__file__)               # Покажет путь к настоящему модулю
print(cv2.__version__)           # Убедись, что версия адекватная

cap = cv2.VideoCapture(0)
print(cap.isOpened())
cap.release()



cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Не удалось открыть поток")
else:
    print("Поток успешно открыт")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Поток прерван или не удалось получить кадр")
            break

        cv2.imshow("RTSP Stream", frame)

        # Закрыть по нажатию Esc
        if cv2.waitKey(1) == 27:
            break

cap.release()
cv2.destroyAllWindows()
