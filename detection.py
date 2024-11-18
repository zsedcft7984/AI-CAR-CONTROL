from urllib.request import urlopen

class Detection:
    def __init__(self, camera_stream, ip):
        self.camera_stream = camera_stream
        self.ip = ip
        self.face_detection_enabled = False
        self.line_following_enabled = False
        self.yolo_enabled = False

    def set_speed(self, speed):
        urlopen(f'http://{self.ip}/action?go=speed{speed}')
    
    def forward(self):
        urlopen(f'http://{self.ip}/action?go=forward')
    def backward(self):
        urlopen(f'http://{self.ip}/action?go=backward')
    def left(self):
        urlopen(f'http://{self.ip}/action?go=left')
    def right(self):
        urlopen(f'http://{self.ip}/action?go=right')
    def stop(self):
        urlopen(f'http://{self.ip}/action?go=stop')
