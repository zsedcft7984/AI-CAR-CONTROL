import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from detection import Detection
from camera_stream import CameraStream
from button_control import ButtonControl
from ui_layout import UILayout


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        ip = '192.168.137.224'
        self.camera_stream = CameraStream(ip)
        self.detection = Detection(self.camera_stream, ip)
        self.button_control = ButtonControl(self.detection)

        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.video_label = QLabel(self)
        layout = UILayout(self.video_label, self.button_control)
        main_layout = layout.create_main_layout()

        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.setWindowTitle('AI CAR CONTROL WINDOW')
        self.move(600, 200)
        self.resize(400, 300)
        self.show()

    def update_frame(self):
        frame = self.camera_stream.get_frame()
        if frame is not None:
            if self.detection.face_detection_enabled:
                self.detection.perform_face_detection(frame)
            if self.detection.line_following_enabled:
                self.detection.perform_line_following(frame)
            if self.detection.yolo_enabled:
                self.detection.perform_yolo_detection(frame)

            q_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)
        else:
            print("Failed to get frame from the camera stream.")
    def update_frame(self):
        frame = self.camera_stream.get_frame()
        if frame is not None:
            if self.detection.face_detection_enabled:
                self.detection.perform_face_detection(frame)
            if self.detection.line_following_enabled:
                self.detection.perform_line_following(frame)
            if self.detection.yolo_enabled:
                self.detection.perform_yolo_detection(frame)

            q_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        self.button_control.handle_key_event(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
