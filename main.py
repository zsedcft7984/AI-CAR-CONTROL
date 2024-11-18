import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from UILayoutManager import UILayoutManager
from CarController import CarController
import cv2
import numpy as np
from urllib.request import urlopen

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ip = '192.168.137.224'
        self.car_controller = CarController(self.ip)
        self.stream = urlopen(f'http://{self.ip}:81/stream')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)
        self.initUI()

    def initUI(self):
        """UI를 초기화합니다."""
        widget = QWidget()
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setGeometry(0, 0, 400, 600)

        # 레이아웃 및 버튼 설정
        self.first_layout = UILayoutManager.create_speed_buttons(self, self.car_controller.set_speed)
        btn_forward, btn_backward, btn_left, btn_right, btn_stop = UILayoutManager.create_direction_buttons(self, {
            "forward": self.car_controller.forward,
            "backward": self.car_controller.backward,
            "left": self.car_controller.left,
            "right": self.car_controller.right,
            "stop": self.car_controller.stop
        })

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout(widget)
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(self.first_layout)
        main_layout.addLayout(UILayoutManager.create_button_layout(btn_forward))
        main_layout.addLayout(UILayoutManager.create_button_layout(btn_left, btn_stop, btn_right))
        main_layout.addLayout(UILayoutManager.create_button_layout(btn_backward))

        self.setCentralWidget(widget)
        self.setWindowTitle('AI CAR CONTROL WINDOW')
        self.move(600, 200)
        self.resize(400, 300)
        self.show()

    def update_frame(self):
        """비디오 프레임을 업데이트합니다."""
        buffer = b""
        buffer += self.stream.read(4096)
        head = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')

        if head > -1 and end > -1:
            jpg = buffer[head:end+2]
            buffer = buffer[end+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            img = cv2.flip(img, -1)

            # 프레임 변환 후 표시
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channels = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        """키 입력 이벤트 처리."""
        if event.key() == Qt.Key_W:
            self.car_controller.forward()
        elif event.key() == Qt.Key_S:
            self.car_controller.backward()
        elif event.key() == Qt.Key_A:
            self.car_controller.left()
        elif event.key() == Qt.Key_D:
            self.car_controller.right()
        elif event.key() == Qt.Key_R:
            self.car_controller.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
