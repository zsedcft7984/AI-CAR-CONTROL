# ui_layout.py

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

class UILayout:
    def __init__(self, video_label, button_control):
        self.video_label = video_label
        self.button_control = button_control

    def create_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(self.button_control.create_speed_buttons())
        main_layout.addLayout(self.button_control.create_direction_buttons())
        main_layout.addWidget(self.button_control.face_detection_button)
        main_layout.addWidget(self.button_control.line_following_button)
        main_layout.addWidget(self.button_control.yolo_detection_button)
        return main_layout
