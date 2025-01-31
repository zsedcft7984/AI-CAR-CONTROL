# AI CAR CONTROL WINDOW

이 프로그램은 PyQt5를 사용하여 로봇 차를 제어하고 실시간 비디오 스트리밍을 제공하는 GUI 애플리케이션입니다. 사용자는 UI에서 버튼을 통해 차의 속도 및 방향을 조정하고, 키보드 입력으로도 차를 제어할 수 있습니다.

## 주요 기능

- **실시간 비디오 스트리밍**: 로봇 차에서 실시간으로 전송되는 영상을 GUI 화면에 표시.
- **방향 제어**: 사용자는 버튼을 통해 로봇 차를 전진, 후진, 좌회전, 우회전 및 정지할 수 있습니다.
- **속도 조절**: 여러 속도 버튼을 통해 로봇 차의 속도를 제어할 수 있습니다.
- **키보드 제어**: 키보드의 W, A, S, D, R 키로 차를 제어할 수 있습니다.

## 설치 및 실행

### 1. 필수 라이브러리 설치

이 프로그램을 실행하려면 `PyQt5`, `opencv-python`, `numpy`가 필요합니다. 아래 명령어를 통해 설치할 수 있습니다.

```bash
pip install pyqt5 opencv-python numpy
```

### 2. 프로그램 실행
설치가 완료되면, 아래 명령어를 입력하여 프로그램을 실행할 수 있습니다.

```bash
python app.py
```

## 코드 설명

# 1. App 클래스

`App` 클래스는 PyQt5의 `QMainWindow`를 상속받아 UI를 구성하고, 실시간 비디오 스트리밍을 처리하며, 로봇 차의 제어 기능을 구현합니다.

## 속성

- **ip**: 로봇 차의 IP 주소
- **car_controller**: `CarController` 객체로 로봇 차의 제어를 담당
- **stream**: 로봇 차에서 전송하는 스트리밍 URL을 통해 비디오 스트림을 읽음
- **timer**: 일정 주기로 `update_frame` 메서드를 호출하여 비디오 프레임을 업데이트함

## 주요 메서드

### UI 초기화
`initUI` 메서드는 로봇 차의 방향 제어 및 속도 조절을 위한 버튼들을 레이아웃에 배치합니다.

### 프레임 업데이트
`update_frame` 메서드는 스트리밍된 비디오 데이터를 받아와 화면에 표시합니다.

### 키보드 이벤트 처리
`keyPressEvent` 메서드는 W, A, S, D, R 키 입력에 따라 로봇 차를 제어합니다.

### 2. CarController 클래스
CarController는 로봇 차의 움직임을 제어하는 클래스입니다. 이 클래스는 차의 방향과 속도를 조절하는 메서드를 포함합니다.

forward: 차를 전진시킴
backward: 차를 후진시킴
left: 차를 좌회전시킴
right: 차를 우회전시킴
stop: 차를 정지시킴
### 3. 비디오 스트리밍 처리
update_frame 메서드는 URL에서 실시간으로 비디오 스트리밍을 받아와 OpenCV를 사용하여 이미지를 디코딩하고 화면에 표시합니다.

### 4. UI 레이아웃
UI 레이아웃은 UILayoutManager 클래스를 통해 구성됩니다. 이 클래스는 버튼 배열과 방향 제어 버튼을 UI에 배치하는 역할을 합니다.

키보드 제어
W: 전진
S: 후진
A: 좌회전
D: 우회전
R: 정지
## 주의사항
로봇 차는 특정 IP 주소로 연결되므로, self.ip를 실제 로봇 차의 IP 주소로 변경해야 합니다.
실시간 스트리밍은 HTTP 프로토콜을 통해 전송되므로, 네트워크 연결 상태가 원활해야 합니다.
