# ui/mainTab.py

import asyncio
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QPushButton, QToolBar, QMessageBox
from PyQt5.QtCore import Qt

from video_control.application.services.AuthService import AuthService
from video_control.application.services.ConfigEditor import ConfigEditor
from video_control.application.services.ShelvingService import ShelvingService
from video_control.application.videocamers.CameraService import CameraService
from video_control.application.videocamers.StreamService import StreamService

from .widgets.ConfigTab import ConfigTab
from .widgets.CameraListTab import CameraListTab
from .widgets.MappingTab import MappingTab


class MainWindow(QMainWindow):
    def __init__(
        self,
        auth_service: AuthService,
        camera_service: CameraService,
        shelving_service: ShelvingService,
        stream_service: StreamService,
        config_editor: ConfigEditor
    ):
        super().__init__()
        self.setWindowTitle("Camera Client")
        self.resize(800, 600)

        self.auth_service     = auth_service
        self.camera_service   = camera_service
        self.shelving_service = shelving_service
        self.stream_service   = stream_service
        self.config_editor    = config_editor

        # === Создаём QTabWidget ===
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

        # === Статические вкладки ===
        self.config_tab      = ConfigTab(
            config_editor=self.config_editor,
            auth_service=self.auth_service,
            parent=self
        )
        self.camera_list_tab = CameraListTab(
            camera_service=self.camera_service,
            parent=self
        )
        self.mapping_tab     = MappingTab(
            camera_service=self.camera_service,
            shelving_service=self.shelving_service,
            parent=self
        )

        self.tabs.addTab(self.config_tab,      "Конфигурация")
        self.tabs.addTab(self.camera_list_tab, "Список камер")
        self.tabs.addTab(self.mapping_tab,     "Сопоставление")

        # === Toolbar Старт/Стоп потока ===
        toolbar = QToolBar("Stream")
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        self.btn_start = QPushButton("Старт потока")
        self.btn_stop  = QPushButton("Стоп потока")
        self.btn_start.clicked.connect(self._on_start_stream)
        self.btn_stop.clicked.connect(self._on_stop_stream)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        toolbar.addWidget(self.btn_start)
        toolbar.addWidget(self.btn_stop)

        # Когда пользователь сохранит маппинг, активируем кнопки
        self.mapping_tab.mapping_saved.connect(self._enable_stream_buttons)

        # === Автозапуск, если конфигурация уже есть ===
        self._auto_restore_state()

    def _enable_stream_buttons(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(True)

    def _on_start_stream(self):
        try:
            self.stream_service.start()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить поток:\n{e}")

    def _on_stop_stream(self):
        self.stream_service.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def add_stream_tab(self, widget, title: str):
        """
        Удаляем прошлые динамические табы, затем добавляем новый в конец.
        При удалении сначала закрываем виджет, чтобы остановить поток.
        """
        while self.tabs.count() > 3:
            old_widget = self.tabs.widget(3)
            old_widget.close()
            self.tabs.removeTab(3)

        idx = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(idx)

    def _on_tab_changed(self, index: int):
        """
        Если переключились на одну из статических вкладок (0–2),
        удаляем все динамические (начиная с индекса 3), 
        предварительно закрыв их.
        """
        if index < 3:
            while self.tabs.count() > 3:
                w = self.tabs.widget(3)
                w.close()
                self.tabs.removeTab(3)

    def _auto_restore_state(self):
        """
        Если в INI есть логин/пароль/код, и камера + маппинги уже сохранены,
        автоматически восстанавливаем состояние без ручного клика.
        """
        if not self.auth_service.is_logined or not bool(asyncio.run(self.camera_service.is_ready)):
            return
        self._enable_stream_buttons()