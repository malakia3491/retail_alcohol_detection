import asyncio
import traceback
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QComboBox, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal

from video_control.application.services.ShelvingService import ShelvingService
from video_control.application.videocamers.CameraService import CameraService
from video_control.domain.Videocamera import Videocamera
from video_control.domain.Shelving import Shelving

class MappingTab(QWidget):
    mapping_saved = pyqtSignal()

    def __init__(
        self,
        camera_service: CameraService,
        shelving_service: ShelvingService,
        parent=None
    ):
        super().__init__(parent)
        self.cam_svc   = camera_service
        self.shelf_svc = shelving_service

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Camera URL", "Shelf Name"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table)

        hl = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self._save)
        hl.addStretch()
        hl.addWidget(self.btn_save)
        layout.addLayout(hl)

        # Кеш для текущих данных
        self._cams    = []
        self._shelves = []

    def showEvent(self, event):
        """
        При каждом показе вкладки перезагружаем камеры и стеллажи.
        """
        super().showEvent(event)
        self._load()

    def _load(self):
        """
        Синхронный обёртка для асинхронной загрузки.
        """
        try:
            # Загружаем списки
            self._cams    = asyncio.run(self.cam_svc.get_all())
            self._shelves = asyncio.run(self.shelf_svc.get_shelvings())

            # Обнуляем таблицу
            self.table.setRowCount(len(self._cams))
            for i, cam in enumerate(self._cams):
                # URL камеры
                item = QTableWidgetItem(cam.url)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 0, item)

                # Комбо для полок
                combo = QComboBox()
                combo.addItems([s.name for s in self._shelves])
                # если уже есть привязка на объекте cam.shelving, то выбираем её
                if cam.shelving:
                    idx = next((j for j, s in enumerate(self._shelves) if s.name == cam.shelving.name), None)
                    if idx is not None:
                        combo.setCurrentIndex(idx)
                self.table.setCellWidget(i, 1, combo)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def _save(self):
        """
        Сохраняем текущие привязки.
        """
        try:
            cams     = []
            shelves  = []
            for r in range(self.table.rowCount()):
                url = self.table.item(r, 0).text()
                shelf_name = self.table.cellWidget(r,1).currentText()
                if not url or not shelf_name:
                    raise ValueError("Все поля должны быть заполнены")
                cam = next(c for c in self._cams if c.url == url)
                shelf = next(s for s in self._shelves if s.name == shelf_name)
                cams.append(cam)
                shelves.append(shelf)

            asyncio.run(self.cam_svc.set_camera_mappings(cams, shelves))
            QMessageBox.information(self, "OK", "Привязки сохранены")
            self.mapping_saved.emit()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", str(e))