import asyncio
import traceback
from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox

from video_control.application.services.AuthService import AuthService
from video_control.application.services.ConfigEditor import ConfigEditor
from video_control.domain.Store import Store

class ConfigTab(QWidget):
    def __init__(self, config_editor: ConfigEditor, auth_service: AuthService, parent=None):
        super().__init__(parent)
        self.editor       = config_editor
        self.auth_service = auth_service

        form = QFormLayout(self)
        # Поля берём из INI (если они там есть)
        self.e_login    = QLineEdit(self.editor.get('auth', 'login', ''))
        self.e_password = QLineEdit(self.editor.get('auth', 'password', ''))
        self.e_password.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Сохранить и авторизоваться")
        btn.clicked.connect(self._on_auth)

        form.addRow("Login:",    self.e_login)
        form.addRow("Password:", self.e_password)
        form.addRow(btn)

    def _on_auth(self):
        login    = self.e_login.text().strip()
        password = self.e_password.text().strip()
        if not (login and password):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            store: Store = asyncio.run(self.auth_service.login(login, password))
            QMessageBox.information(self, "Успех", "Авторизация прошла успешно")
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Ошибка авторизации: {e}")
            return

        self.editor.set_auth(login, password, store.code)
        self.editor.set_store_data(store.id, store.address, store.name)
        
        try:
            self.editor.save()
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфиг: {e}")
