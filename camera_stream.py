import cv2
import numpy as np
from urllib.request import urlopen
from urllib.error import URLError

class CameraStream:
    def __init__(self, ip='192.168.137.224'):
        try:
            self.stream = urlopen(f'http://{ip}:81/stream')
            self.buffer = b""
        except URLError as e:
            print(f"Error connecting to the stream at {ip}: {e}")
            self.stream = None  # 연결 실패 시 stream을 None으로 설정

    def get_frame(self):
        if self.stream is None:
            return None  # 연결 실패 시 None 반환

        self.buffer += self.stream.read(4096)
        head = self.buffer.find(b'\xff\xd8')
        end = self.buffer.find(b'\xff\xd9')
        if head > -1 and end > -1:
            jpg = self.buffer[head:end+2]
            self.buffer = self.buffer[end+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            return cv2.flip(img, -1) if img is not None else None
        return None  # 프레임이 없으면 None 반환
