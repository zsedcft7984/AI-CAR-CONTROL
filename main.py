import sys
import cv2
import os
import threading
import torch
import numpy as np
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from urllib.request import urlopen
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt

# 전역 버퍼
buffer = b""  # 전역 버퍼 초기화

ip = '192.168.137.222'
car_state = 'stop'
urlopen(f'http://{ip}/action?go=speed80')  # 초기 속도 설정

class App(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.stream = urlopen(f'http://{ip}:81/stream')  # 스트림 연결
        
        self.face_detection_enabled = False  # 얼굴 인식 상태 추적 변수
        self.line_following_enabled = False  # 선 추적 상태 추적 변수
        
        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)  # 비디오 중앙 정렬
        self.video_label.setGeometry(0, 0, 400, 600)

        # 비디오 프레임 업데이트 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        # 속도 조정 버튼 생성
        self.create_speed_buttons()

        # 방향 제어 버튼 생성
        btn_forward, btn_backward, btn_left, btn_right, btn_stop = self.create_direction_buttons()

        # 얼굴 인식 토글 버튼
        self.face_detection_button = QPushButton("Toggle Face Detection", self)
        self.face_detection_button.clicked.connect(self.toggle_face_detection)

        # 선 추적 토글 버튼
        self.line_following_button = QPushButton("Toggle Line Following", self)
        self.line_following_button.clicked.connect(self.toggle_line_following)

        # 레이아웃 설정
        main_layout = QVBoxLayout(widget)
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(self.first_layout)   # 속도 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_forward))   # 전진 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_left, btn_stop, btn_right))   # 좌측, 정지, 우측 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_backward))  # 후진 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(self.face_detection_button))  # 얼굴 인식 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(self.line_following_button))  # 선 추적 버튼 레이아웃
        main_layout.addLayout(QHBoxLayout())  # 여백을 위한 빈 레이아웃

        self.setCentralWidget(widget)
        self.setWindowTitle('AI CAR CONTROL WINDOW')
        self.move(600, 200)
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
        # 방향 제어 버튼 생성
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
        global buffer  # 전역 버퍼 사용
        # 비디오 프레임 업데이트
        buffer += self.stream.read(4096)
        head = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')

        try:
            if head > -1 and end > -1:
                jpg = buffer[head:end+2]
                buffer = buffer[end+2:]  # 전역 버퍼 업데이트
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                img = cv2.flip(img, -1)

                # 얼굴 인식이 활성화된 경우
                if self.face_detection_enabled:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

                    if len(faces) > 0:  # 얼굴이 하나 이상 감지된 경우
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            # 얼굴이 감지되면 "Face" 텍스트 표시
                            cv2.putText(img, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # 선 추적이 활성화된 경우
                if self.line_following_enabled:
                    height, width, _ = img.shape
                    img = img[height // 2:, :]

                    # 검은 선 추적을 위한 색상 필터링
                    lower_bound = np.array([0, 0, 0])
                    upper_bound = np.array([255, 255, 80])
                    mask = cv2.inRange(img, lower_bound, upper_bound)

                    cv2.imshow("mask", mask)

                    # 질량 중심 계산
                    M = cv2.moments(mask)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = 0, 0

                    # 이미지 중심과의 거리 계산
                    #center_offset = width // 2 - cX
                    # 디버그 시각화
                    cv2.circle(img, (cX, cY), 10, (0, 255, 0), -1)
                    cv2.imshow("AI CAR Streaming", img)
                # 프레임 변환 후 표시
                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                height, width, channels = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.video_label.setPixmap(pixmap)
        except Exception as e:
            print(e)

    def set_speed(self, speed):
        threading.Thread(target=self.send_speed, args=(speed,)).start()  # 별도의 스레드에서 실행
        print(f'Speed set to {speed}')

    def send_speed(self, speed):
        urlopen(f'http://{ip}/action?go=speed{speed}')

    # 방향 명령
    def forward(self):
        threading.Thread(target=self.send_command, args=('forward',)).start()

    def backward(self):
        threading.Thread(target=self.send_command, args=('backward',)).start()

    def left(self):
        threading.Thread(target=self.send_command, args=('left',)).start()

    def right(self):
        threading.Thread(target=self.send_command, args=('right',)).start()

    def stop(self):
        threading.Thread(target=self.send_command, args=('stop',)).start()

    def send_command(self, direction):
        urlopen(f'http://{ip}/action?go={direction}')
    
    # 얼굴 인식 토글
    def toggle_face_detection(self):
        self.face_detection_enabled = not self.face_detection_enabled
        print(f'Face detection {"enabled" if self.face_detection_enabled else "disabled"}')

    # 선 추적 토글
    def toggle_line_following(self):
        self.line_following_enabled = not self.line_following_enabled
        print(f'Line following {"enabled" if self.line_following_enabled else "disabled"}')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # Esc키 = 창 닫기
            self.close()  # 창을 닫는다.
        elif event.key() == Qt.Key_W:  # W키 = 전진
            self.forward()
        elif event.key() == Qt.Key_S:  # S키 = 후진
            self.backward()
        elif event.key() == Qt.Key_A:  # A키 = 좌회전
            self.left()
        elif event.key() == Qt.Key_D:  # D키 = 우회전
            self.right()
        elif event.key() == Qt.Key_Space:  # Space키 = 정지
            self.stop()
        elif event.key() == Qt.Key_1:
            self.set_speed(40)
        elif event.key() == Qt.Key_2:
            self.set_speed(50)
        elif event.key() == Qt.Key_3:
            self.set_speed(60)
        elif event.key() == Qt.Key_4:
            self.set_speed(80)
        elif event.key() == Qt.Key_5:
            self.set_speed(100)
    def keyReleaseEvent(self, event):
        if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D]:
            self.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = App()
    sys.exit(app.exec_())
