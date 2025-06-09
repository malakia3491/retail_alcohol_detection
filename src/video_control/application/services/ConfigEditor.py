import configparser
from pathlib import Path
from typing import Any, Optional, Union

from video_control.application.conf.Config import Config
from video_control.application.conf.UrlConfig import UrlConfig

class ConfigEditor:
    def __init__(self, filepath: Union[str, Path], encoding: str = 'utf-8'):
        """
        :param filepath: путь к INI-файлу
        :param encoding: кодировка файла
        """
        self.filepath = Path(filepath)
        self.encoding = encoding
        self._parser = configparser.ConfigParser()
        # Если файл существует — читаем его, иначе начнём с пустого
        if self.filepath.exists():
            self._parser.read(self.filepath, encoding=self.encoding)

    def load_config(self) -> Config:
        """
        Загружает секцию [AUTH] из INI-файла и возвращает Config.
        Если файла нет или секции — возвращает None.
        """
        auth_section = 'auth'
        read_files = self._parser.read(self.filepath, encoding='utf-8')
        if not read_files:
            print(f"[ConfigReader] Файл конфигурации не найден: {self.filepath}")
            return None

        if auth_section not in self._parser:
            print(f"[ConfigReader] Секция [{auth_section}] не найдена в {self.filepath}")
            return None

        sec = self._parser[auth_section]
        return Config(
            id = sec.get('id', fallback=None),
            address = sec.get('address', fallback=None),
            name   = sec.get('name', fallback=None),            
            login   = sec.get('login', fallback=None),
            password= sec.get('password', fallback=None),
            code    = sec.get('code', fallback=None),
        )

    def load_url_config(self) -> UrlConfig:
        """
        Загружает секцию [url] из INI-файла и возвращает UrlConfig.
        Если файла нет или секции — возвращает None.
        """
        read_files = self._parser.read(self.filepath, encoding='utf-8')
        if not read_files:
            print(f"[ConfigReader] Файл конфигурации не найден: {self.filepath}")
            return None

        if 'API' not in self._parser:
            print(f"[ConfigReader] Секция [API] не найдена в {self.filepath}")
            return None

        sec = self._parser['API']
        return UrlConfig(
            base_url=sec.get('BASE_URL', fallback=None),
            retail_url=sec.get('RETAIL_URL', fallback=None),
            video_contorl_url=sec.get('VIDEO_CONTROL_URL', fallback=None),
            auth_url=sec.get('AUTH_URL', fallback=None),
        )

    def set(self, section: str, option: str, value: Any) -> None:
        """
        Добавить или обновить опцию `option` в секции `section`.
        Если секции нет — она будет создана.
        """
        if not self._parser.has_section(section):
            self._parser.add_section(section)
        self._parser.set(section, option, str(value))

    def get(self, section: str, option: str, fallback: Optional[Any] = None) -> Any:
        """
        Получить значение опции; если нет секции или опции — вернуть fallback.
        """
        return self._parser.get(section, option, fallback=fallback)

    def remove_option(self, section: str, option: str) -> bool:
        """
        Удалить опцию. 
        :return: True, если удалено; False, если секция или опция не найдены.
        """
        if self._parser.has_section(section):
            return self._parser.remove_option(section, option)
        return False

    def remove_section(self, section: str) -> bool:
        """
        Удалить всю секцию. 
        :return: True, если удалено; False, если секции не было.
        """
        return self._parser.remove_section(section)

    def save(self, filepath: Optional[Union[str, Path]] = None) -> None:
        """
        Сохранить текущие данные в файл.
        Если передан filepath — сохраняем туда, иначе перезаписываем исходный.
        """
        target = Path(filepath) if filepath else self.filepath
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('w', encoding=self.encoding) as f:
            self._parser.write(f)

    def set_auth(self, login: str = None, password: str = None, code: str = None) -> None:
        if login is not None:
            self.set('auth', 'login', login)
        if password is not None:
            self.set('auth', 'password', password)
        if code is not None:
            self.set('auth', 'code', code)

    def set_store_data(self, id: str = None, address: str = None, name: str = None) -> None:
        if id is not None:
            self.set('auth', 'id', id)
        if address is not None:
            self.set('auth', 'address', address)
        if name is not None:
            self.set('auth', 'name', name)

    def set_url(self, base_url: str = None, timeout: Union[int,str] = None, endpoint: str = None) -> None:
        if base_url is not None:
            self.set('url', 'base_url', base_url)
        if timeout is not None:
            self.set('url', 'timeout', timeout)
        if endpoint is not None:
            self.set('url', 'endpoint', endpoint)