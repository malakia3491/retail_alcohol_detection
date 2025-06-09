import inspect

from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase

class InMemoryCache(CacheBase):
    def __init__(self):
        self._cache = {}
        self._indexes = {}
        self._cls_index_fields = {}
        self._last_index_values = {}

    def get(self, key):
        return self._cache.get(key)

    def get_all(self):
        return list(self._cache.values())

    def contains(self, value):
        if hasattr(value, "id") and value.id is not None:
            return self.get(value.id)
        else:
            for obj in self.get_all():
                if obj == value:
                    return obj
            return None

    def put(self, key, value):
        """
        1) Если key уже был, «чистим» старые индексы (напрямую, как раньше).
        2) Вставляем/переписываем self._cache[key] = value.
        3) Зарегистрируем у объекта связь с этим кэшем (value._register_cache(self)), 
           если он является экземпляром IndexNotifiable.
        4) Обновляем поля-индексы как обычно и запоминаем новые «последние» значения.
        """
        # ——— Шаг A: если ключ уже есть, вытаскиваем старые значения, чтобы удалить из индексов ———
        if key in self._cache:
            old_values = self._last_index_values.get(key, {})
            for field_name, old_val in old_values.items():
                idx_map = self._indexes.get(field_name)
                if idx_map is not None and old_val in idx_map:
                    del idx_map[old_val]

        # ——— Шаг B: кладём в основной кэш — self._cache[key] = value ———
        self._cache[key] = value

        # ——— Шаг C: если value умеет регистрироваться в кэше, регистрируем ———
        if isinstance(value, IndexNotifiable):
            value._register_cache(self)

        # ——— Шаг D: если новый класс — дергаем рефлексию и запоминаем поля-индексы ———
        cls = type(value)
        if cls not in self._cls_index_fields:
            index_fields = []
            for name, member in inspect.getmembers(cls):
                # если свойство через @property и помечено @indexed
                if isinstance(member, property) and getattr(member.fget, "_is_indexed", False):
                    index_fields.append(name)
                # если это простой метод и он помечен @indexed
                elif callable(member) and getattr(member, "_is_indexed", False):
                    index_fields.append(name)
            self._cls_index_fields[cls] = index_fields

        index_fields = self._cls_index_fields[cls]

        # ——— Шаг E: перебираем каждое индексное поле, кладём „value → объект“ в self._indexes ———
        new_index_values = {}
        for field_name in index_fields:
            member = getattr(cls, field_name)
            new_val = None
            if isinstance(member, property):
                new_val = getattr(value, field_name)
            else:
                # обычный метод, вызываем
                method = getattr(value, field_name)
                if callable(method):
                    new_val = method()

            if new_val is None:
                continue

            if field_name not in self._indexes:
                self._indexes[field_name] = {}
            self._indexes[field_name][new_val] = value
            new_index_values[field_name] = new_val

        # ——— Шаг F: сохраняем «новые» значения полей
        self._last_index_values[key] = new_index_values

    def clear(self):
        self._cache.clear()
        self._indexes.clear()
        self._cls_index_fields.clear()
        self._last_index_values.clear()

    def __len__(self):
        return len(self._cache)

    @property
    def ids(self):
        return self._cache.keys()

    def in_cache(self, *ids):
        in_ids = []
        not_in_ids = []
        for _id in ids:
            if _id in self.ids:
                in_ids.append(_id)
            else:
                not_in_ids.append(_id)
        return in_ids, not_in_ids

    def get_by(self, field, value):
        return self._indexes.get(field, {}).get(value)

    # ——— НОВЫЙ метод, который вызывается из объекта при смене поля ———
    def _update_index_on_field_change(self, obj, field_name, old_value, new_value):
        """
        obj            — тот же объект, который хранится в self._cache
        field_name     — строка (имя помеченного @indexed поля)
        old_value      — старое значение, по которому ранее лежало «field_name→obj» в индексе
        new_value      — новое значение для этого же поля

        Нужно:
         1) Удалить из self._indexes[field_name][old_value] (если было)
         2) Положить self._indexes[field_name][new_value] = obj
         3) Обновить self._last_index_values у ключа, по которому obj лежит в основном кэше
        """
        # а) Найти ключ, под которым в основном кэше хранится obj
        #    (мы храним в self._cache: key → объект, 
        #     но нам здесь надо узнать сам key, потому что если
        #     у одного объекта несколько свойств-индексов, нам надо знать,
        #     к какому именно ключу обновлять self._last_index_values[key])
        #    
        # Самый прямой (хоть и не самый эффективный) способ — линейный перебор:
        cache_key = None
        for k, v in self._cache.items():
            if v is obj:
                cache_key = k
                break

        if cache_key is None:
            # Объект не зарегистрирован в этом кэше (странно),
            # просто игнорируем
            return

        idx_map = self._indexes.get(field_name)
        if idx_map is not None and old_value in idx_map:
            del idx_map[old_value]

        if field_name not in self._indexes:
            self._indexes[field_name] = {}
        self._indexes[field_name][new_value] = obj

        if cache_key not in self._last_index_values:
            self._last_index_values[cache_key] = {}
        self._last_index_values[cache_key][field_name] = new_value