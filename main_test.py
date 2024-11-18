# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer
from urllib.request import urlopen
from key_control import KeyControl  # KeyControl 모듈 import

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ip = '192.168.137.224'
        self.stream = urlopen(f'http://{self.ip}:81/stream')
        self.car_state = 'stop'
        
        self.key_control = KeyControl(self, self.ip)  # KeyControl 객체 생성

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.video_label = QLabel(self)
        layout = QVBoxLayout(widget)
        layout.addWidget(self.video_label)

        self.setCentralWidget(widget)
        self.setWindowTitle('AI CAR CONTROL WINDOW')
        self.move(600, 200)
        self.resize(400, 300)
        self.show()

    def update_frame(self):
        # 기존 코드 그대로 (비디오 프레임 업데이트)
        pass

    def forward(self):
        if self.car_state != 'forward':
            urlopen(f'http://{self.ip}/action?go=forward')
            self.car_state = 'forward'

    def backward(self):
        if self.car_state != 'backward':
            urlopen(f'http://{self.ip}/action?go=backward')
            self.car_state = 'backward'

    def left(self):
        if self.car_state != 'left':
            urlopen(f'http://{self.ip}/action?go=left')
            self.car_state = 'left'

    def right(self):
        if self.car_state != 'right':
            urlopen(f'http://{self.ip}/action?go=right')
            self.car_state = 'right'

    def stop(self):
        if self.car_state != 'stop':
            urlopen(f'http://{self.ip}/action?go=stop')
            self.car_state = 'stop'

    def set_speed(self, speed):
        urlopen(f'http://{self.ip}/action?go=speed{speed}')

    def toggle_face_detection(self):
        # 얼굴 인식 토글 함수
        pass

    def toggle_line_following(self):
        # 선 추적 토글 함수
        pass

    def toggle_yolo_detection(self):
        # YOLO 토글 함수
        pass

    def keyPressEvent(self, event):
        self.key_control.handle_key_event(event)  # KeyControl에서 키 이벤트 처리

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
