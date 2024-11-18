from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class ButtonControl:
    def __init__(self, detection):
        self.detection = detection
        self.face_detection_button = QPushButton("Toggle Face Detection")
        self.line_following_button = QPushButton("Toggle Line Following")
        self.yolo_detection_button = QPushButton("Toggle YOLO Detection")

        self.face_detection_button.clicked.connect(self.detection.toggle_face_detection)
        self.line_following_button.clicked.connect(self.detection.toggle_line_following)
        self.yolo_detection_button.clicked.connect(self.detection.toggle_yolo_detection)

    def create_speed_buttons(self):
        layout = QHBoxLayout()
        for speed in [40, 50, 60, 80, 100]:
            btn = QPushButton(f'SPEED {speed}')
            btn.clicked.connect(lambda _, s=speed: self.detection.set_speed(s))
            layout.addWidget(btn)
        return layout

    def create_direction_buttons(self):
        layout = QHBoxLayout()
        for label, handler in [('FORWARD', self.detection.forward),
                               ('LEFT', self.detection.left),
                               ('STOP', self.detection.stop),
                               ('RIGHT', self.detection.right),
                               ('BACKWARD', self.detection.backward)]:
            btn = QPushButton(label)
            btn.pressed.connect(handler)
            btn.released.connect(self.detection.stop)
            layout.addWidget(btn)
        return layout

    def handle_key_event(self, event):
        key_mappings = {
            Qt.Key_W: self.detection.forward,
            Qt.Key_S: self.detection.backward,
            Qt.Key_A: self.detection.left,
            Qt.Key_D: self.detection.right,
            Qt.Key_R: self.detection.stop,
            Qt.Key_F: self.detection.toggle_face_detection,
            Qt.Key_M: self.detection.toggle_line_following,
            Qt.Key_Y: self.detection.toggle_yolo_detection
        }
        if event.key() in key_mappings:
            key_mappings[event.key()]()
