import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from urllib.request import urlopen
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
import cv2
import numpy as np


class App(QMainWindow):
    ip = '192.168.137.238'

    def __init__(self):
        super().__init__()
        self.stream = urlopen(f'http://{App.ip}:81/stream')  # 스트림 연결
        self.buffer = b""  # 버퍼 초기화

        urlopen(f'http://{App.ip}/action?go=speed80')  # 초기 속도 설정
        self.face_detection_enabled = False  # 얼굴 인식 상태를 추적하는 변수
        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)  # 비디오를 중앙에 정렬
        self.video_label.setGeometry(0, 0, 400, 600)

        # 비디오 프레임 업데이트를 위한 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        # 속도 조절 버튼 생성
        self.create_speed_buttons()

        # 방향 조절 버튼 생성
        btn_forward, btn_backward, btn_left, btn_right, btn_stop = self.create_direction_buttons()

        # 얼굴 인식 토글 버튼
        self.face_detection_button = QPushButton("Toggle Face Detection", self)
        self.face_detection_button.clicked.connect(self.toggle_face_detection)

        # 레이아웃 설정
        main_layout = QVBoxLayout(widget)
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(self.first_layout)   # 속도 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_forward))   # 전진 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_left, btn_stop, btn_right))   # 좌, 정지, 우 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_backward))  # 후진 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(self.face_detection_button))  # 얼굴 인식 버튼 레이아웃
        main_layout.addLayout(QHBoxLayout())  # 여백을 위한 빈 레이아웃

        self.setCentralWidget(widget)
        self.setWindowTitle('AI CAR CONTROL WINDOW')
        self.move(600, 400)
        self.resize(400, 300)
        self.show()

    def create_speed_buttons(self):
        # 속도 버튼 레이아웃
        speed_buttons = [40, 50, 60, 80, 100]
        self.first_layout = QHBoxLayout()
        for speed in speed_buttons:
            btn = QPushButton(f'SPEED {speed}', self)
            btn.clicked.connect(lambda _, s=speed: self.set_speed(s))
            self.first_layout.addWidget(btn)

    def create_direction_buttons(self):
        # 방향 조절 버튼 생성
        btn_forward = QPushButton('FORWARD', self)
        btn_backward = QPushButton('BACKWARD', self)
        btn_left = QPushButton('LEFT', self)
        btn_right = QPushButton('RIGHT', self)
        btn_stop = QPushButton('STOP', self)

        btn_forward.pressed.connect(self.forward)
        btn_forward.released.connect(self.stop)
        btn_backward.pressed.connect(self.backward)
        btn_backward.released.connect(self.stop)

        btn_left.pressed.connect(self.left)
        btn_left.released.connect(self.stop)
        btn_right.pressed.connect(self.right)
        btn_right.released.connect(self.stop)
        btn_stop.pressed.connect(self.stop)

        return btn_forward, btn_backward, btn_left, btn_right, btn_stop

    def create_button_layout(self, *buttons):
        layout = QHBoxLayout()
        for button in buttons:
            layout.addWidget(button)
        return layout

    def update_frame(self):
        # 비디오 프레임 업데이트
        self.buffer += self.stream.read(4096)
        head = self.buffer.find(b'\xff\xd8')
        end = self.buffer.find(b'\xff\xd9')

        try:
            if head > -1 and end > -1:
                jpg = self.buffer[head:end+2]
                self.buffer = self.buffer[end+2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                img = cv2.flip(img, -1)

                # 얼굴 인식이 활성화되었으면 얼굴 인식 수행
                if self.face_detection_enabled:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                    if len(faces) > 0:  # 얼굴이 하나 이상 감지되었을 경우
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            # 얼굴이 인식되었으면 "Face" 텍스트를 표시
                            cv2.putText(img, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # 프레임을 디스플레이용으로 변환
                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                height, width, channels = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.video_label.setPixmap(pixmap)
        except Exception as e:
            print(e)

    def set_speed(self, speed):
        urlopen(f'http://{App.ip}/action?go=speed{speed}')
        print(f'Speed set to {speed}')

    # 방향 명령
    def forward(self):
        urlopen(f'http://{App.ip}/action?go=forward')

    def backward(self):
        urlopen(f'http://{App.ip}/action?go=backward')

    def left(self):
        urlopen(f'http://{App.ip}/action?go=left')

    def right(self):
        urlopen(f'http://{App.ip}/action?go=right')

    def stop(self):
        urlopen(f'http://{App.ip}/action?go=speed80')
        urlopen(f'http://{App.ip}/action?go=stop')

    def toggle_face_detection(self):
        """얼굴 인식 상태를 토글 (켜기/끄기)"""
        self.face_detection_enabled = not self.face_detection_enabled
        if self.face_detection_enabled:
            print("Face Detection Activated")
        else:
            print("Face Detection Deactivated")

    # 키보드 이벤트 처리 (이동)
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W :
            self.forward()
        elif key == Qt.Key_S:
            self.backward()
        elif key == Qt.Key_A:
            self.left()
        elif key == Qt.Key_D:
            self.right()
        elif key == Qt.Key_R:
            self.stop()

    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = App()
    sys.exit(app.exec_())
