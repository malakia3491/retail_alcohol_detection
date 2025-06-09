import asyncio
import cv2

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QLabel
)

from video_control.application.videocamers.CameraService import CameraService
from video_control.domain.Videocamera import Videocamera

class VideoStreamTab(QWidget):
    def __init__(self, rtsp_url: str, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout(self))
        self.label = QLabel("Starting...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.label)

        # Запускаем поток
        self.thread = VideoThread(rtsp_url, self)
        self.thread.frame_ready.connect(self.on_frame)
        self.thread.start()

    def on_frame(self, img: QImage):
        self.label.setPixmap(QPixmap.fromImage(img).scaled(
            self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def closeEvent(self, event):
        self.thread.stop()
        super().closeEvent(event)

class CameraTester(QThread):
    result = pyqtSignal(int, bool, str)

    def __init__(self, cams: list[Videocamera], svc: CameraService, parent=None):
        super().__init__(parent)
        self.cams = cams
        self.svc  = svc

    def run(self):
        for idx, cam in enumerate(self.cams):
            ok, msg = asyncio.run(self.svc.test_camera(cam))
            self.result.emit(idx, ok, msg)

class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить камеру")
        form = QFormLayout(self)
        self.ip     = QLineEdit()
        self.port   = QLineEdit("8554")
        self.user   = QLineEdit()
        self.passwd = QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        form.addRow("IP адрес:", self.ip)
        form.addRow("Порт:",    self.port)
        form.addRow("User:",    self.user)
        form.addRow("Password:",self.passwd)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self):
        return {
            'ip':       self.ip.text().strip(),
            'port':     int(self.port.text().strip()),
            'username': self.user.text().strip(),
            'password': self.passwd.text().strip()
        }

class VideoThread(QThread):
    frame_ready = pyqtSignal(QImage)

    def __init__(self, rtsp_url: str, parent=None):
        super().__init__(parent)
        self.url = rtsp_url
        self._running = True

    def run(self):
        cap = cv2.VideoCapture(self.url)
        while self._running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(img)
            self.msleep(30)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()

class VideoStreamWindow(QWidget):
    def __init__(self, rtsp_url: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Stream: {rtsp_url}")
        self.resize(640, 480)
        self.label = QLabel("Starting...", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.thread = VideoThread(rtsp_url, self)
        self.thread.frame_ready.connect(self.on_frame)
        self.thread.start()

    def on_frame(self, img: QImage):
        self.label.setPixmap(QPixmap.fromImage(img).scaled(
            self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def closeEvent(self, event):
        self.thread.stop()
        super().closeEvent(event)


class CameraListTab(QWidget):
    def __init__(self, camera_service: CameraService, parent=None):
        super().__init__(parent)
        self.svc = camera_service
        layout = QVBoxLayout(self)

        # Таблица: IP, Port, User, Status
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["IP", "Port", "User", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellDoubleClicked.connect(self.on_row_activated)
        layout.addWidget(self.table)

        # Кнопки
        hl = QHBoxLayout()
        btn_add  = QPushButton("Добавить камеру")
        btn_test = QPushButton("Проверить подключение")
        btn_add.clicked.connect(self.on_add)
        btn_test.clicked.connect(self.on_test)
        hl.addWidget(btn_add)
        hl.addWidget(btn_test)
        hl.addStretch()
        layout.addLayout(hl)

        # Загрузим из репозитория
        asyncio.run(self._load_existing())

    async def _load_existing(self):
        cams = await self.svc.get_all()
        for cam in cams:
            self._add_row(cam)

    def _add_row(self, cam: Videocamera):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(cam.ip))
        self.table.setItem(row, 1, QTableWidgetItem(str(cam.port)))
        self.table.setItem(row, 2, QTableWidgetItem(cam.username or ""))
        status = QTableWidgetItem("—")
        status.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, status)

    def on_add(self):
        dlg = AddCameraDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            cam = asyncio.run(self.svc.add_camera(
                data['ip'], data['port'],
                data['username'], data['password']
            ))
            self._add_row(cam)

    def on_test(self):
        rows = self.table.rowCount()
        if rows == 0:
            QMessageBox.information(self, "Проверка", "Нет камер для проверки")
            return
        for r in range(rows):
            item = self.table.item(r, 3)
            item.setText("…"); item.setBackground(QColor("lightgray"))
        cams = asyncio.run(self.svc.get_all())
        tester = CameraTester(cams, self.svc, self)
        tester.result.connect(self._on_result)
        tester.start()

    def _on_result(self, row: int, ok: bool, msg: str):
        item = self.table.item(row, 3)
        item.setText("OK" if ok else "FAIL")
        item.setBackground(QColor("lightgreen") if ok else QColor("lightcoral"))
        item.setToolTip(msg)

    def on_row_activated(self, row: int, col: int):
            status_item = self.table.item(row, 3)
            status = status_item.text()
            cam = asyncio.run(self.svc.get_all())[row]

            # если тест ещё не делали или не OK — запустить проверку
            if status != "OK":
                ok, msg = asyncio.run(self.svc.test_camera(cam))
                self._on_result(row, ok, msg)
                if not ok:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось подключиться:\n{msg}")
                    return

            # Создаем вкладку с видеопотоком
            rtsp_url = cam.url
            stream_tab = VideoStreamTab(rtsp_url, parent=self)

            # Получаем QTabWidget из MainWindow
            main_win = self.window()
            # Предполагается, что MainWindow хранит `self.tabs`
            tab_widget = main_win.tabs

            # Добавляем вкладку
            index = tab_widget.addTab(stream_tab, f"Stream {cam.ip}")
            tab_widget.setCurrentIndex(index)