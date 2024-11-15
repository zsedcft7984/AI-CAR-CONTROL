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


class App(QMainWindow):
    ip = '192.168.137.222'
    
    def __init__(self):
        super().__init__()
        self.stream = urlopen(f'http://{App.ip}:81/stream')  # 스트림 연결
        self.buffer = b""  # 버퍼 초기화

        urlopen(f'http://{App.ip}/action?go=speed80')  # 초기 속도 설정
        self.face_detection_enabled = False  # 얼굴 인식 상태를 추적하는 변수
        self.line_following_enabled = False  # 라인트레이싱 상태 추적 변수
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

        # 라인트레이싱 토글 버튼
        self.line_following_button = QPushButton("Toggle Line Following", self)
        self.line_following_button.clicked.connect(self.toggle_line_following)

        # 레이아웃 설정
        main_layout = QVBoxLayout(widget)
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(self.first_layout)   # 속도 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_forward))   # 전진 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_left, btn_stop, btn_right))   # 좌, 정지, 우 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(btn_backward))  # 후진 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(self.face_detection_button))  # 얼굴 인식 버튼 레이아웃
        main_layout.addLayout(self.create_button_layout(self.line_following_button))  # 라인트레이싱 버튼 레이아웃
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
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

                    if len(faces) > 0:  # 얼굴이 하나 이상 감지되었을 경우
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            # 얼굴이 인식되었으면 "Face" 텍스트를 표시
                            cv2.putText(img, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # 라인트레이싱이 활성화되었으면 라인트레이싱 알고리즘 적용
                if self.line_following_enabled:
                    height, width, _ = img.shape
                    img = img[height // 2:, :]
                    
                    # 색상 필터링으로 검정색 선 추출
                    #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    lower_bound = np.array([0, 0, 0])
                    upper_bound = np.array([255, 255, 80])
                    mask = cv2.inRange(img, lower_bound, upper_bound)

                    cv2.imshow("mask", mask)
                    
                    # 무게 중심 계산
                    M = cv2.moments(mask)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = 0, 0
                    
                    # 무게 중심과 이미지 중앙의 거리 계산
                    center_offset = width // 2 - cX
                    #print(center_offset)

                    # 디버그용 시각화
                    cv2.circle(img, (cX, cY), 10, (0, 255, 0), -1)
                    cv2.imshow("AI CAR Streaming", img)


                    if center_offset > 10:
                        x = "right"
                        #urlopen('http://' + ip + "/action?go=right")
                    elif center_offset < -10:
                        car_state = "left"
                        #urlopen('http://' + ip + "/action?go=left")
                    else:
                        car_state = "go"
                        #urlopen('http://' + ip + "/action?go=forward")


                    # 여기에 라인트레이싱 알고리즘을 추가
                    # 예: 간단한 라인 추적을 위해 화면에서 라인 감지 및 따라가기
                    # 이 부분을 실제 라인트레이싱 코드로 구현해야 함

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

    def toggle_line_following(self):
        """라인 추적 상태를 토글 (켜기/끄기)"""
        self.line_following_enabled = not self.line_following_enabled
        if self.line_following_enabled:
            print("Line Following Activated")
        else:
            print("Line Following Deactivated")
            # 라인트레이싱 종료 후 창 닫기
            cv2.destroyWindow("Line Following")  # OpenCV 창을 종료
            # 여기서 라인트레이싱에 관련된 다른 종료 작업을 추가할 수 있음

    # 키보드 이벤트 처리 (이동)
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W:
            self.forward()
        elif key == Qt.Key_S:
            self.backward()
        elif key == Qt.Key_A:
            self.left()
        elif key == Qt.Key_D:
            self.right()
        elif key == Qt.Key_R:
            self.stop()
        elif key == Qt.Key_Q:
            self.toggle_face_detection()
        elif key == Qt.Key_E:
            self.toggle_line_following()

    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = App()
    sys.exit(app.exec_())
