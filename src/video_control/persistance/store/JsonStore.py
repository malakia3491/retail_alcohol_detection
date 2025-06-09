import json
from typing import List

class JsonStore:
    def __init__(self, filepath: str):
        """
        :param filepath: путь к JSON-файлу, в котором будут храниться данные
        """
        self._filepath = filepath

    def save(self, objs: List[dict]) -> None:
        """
        Сохраняет список видеокамер в JSON-файл.
        """
        with open(self._filepath, 'w', encoding='utf-8') as f:
            json.dump(objs, f, ensure_ascii=False, indent=4)

    def load(self) -> List[dict]:
        """
        Загружает список видеокамер из JSON-файла.
        Если файл не найден или пустой — возвращает пустой список.
        """
        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []