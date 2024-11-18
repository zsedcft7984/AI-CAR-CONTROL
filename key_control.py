# key_control.py
from PyQt5.QtCore import Qt
from urllib.request import urlopen

class KeyControl:
    def __init__(self, app, ip):
        self.app = app
        self.ip = ip

    def handle_key_event(self, event):
        if event.key() == Qt.Key_Escape:  # Esc키 = 창 닫기
            urlopen(f'http://{self.ip}/action?go=stop')
            self.app.close()  # 창을 닫는다.
        elif event.key() == Qt.Key_W:  # W키 = 전진
            self.app.forward()
        elif event.key() == Qt.Key_S:  # S키 = 후진
            self.app.backward()
        elif event.key() == Qt.Key_A:  # A키 = 좌회전
            self.app.left()
        elif event.key() == Qt.Key_D:  # D키 = 우회전
            self.app.right()
        elif event.key() == Qt.Key_R:  # 'R' 키가 눌리면 정지
            self.app.stop()

        elif event.key() == Qt.Key_1:
            self.app.set_speed(40)
        elif event.key() == Qt.Key_2:
            self.app.set_speed(50)
        elif event.key() == Qt.Key_3:
            self.app.set_speed(60)
        elif event.key() == Qt.Key_4:
            self.app.set_speed(80)
        elif event.key() == Qt.Key_5:
            self.app.set_speed(100)
        elif event.key() == Qt.Key_F:  # F키 = 얼굴 인식 토글
            self.app.toggle_face_detection()
        elif event.key() == Qt.Key_M:  # M키 = 자동주행 토글
            self.app.toggle_line_following()
        elif event.key() == Qt.Key_Y:
            self.app.toggle_yolo_detection()
