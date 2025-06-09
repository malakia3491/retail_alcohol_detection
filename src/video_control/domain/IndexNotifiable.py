from video_control.persistance.cache.CacheBase import CacheBase

def indexed(obj):
    """
    Если obj – property, помечаем obj.fget.
    Иначе obj – обычная функция (геттер или метод) – помечаем её напрямую.
    """
    if isinstance(obj, property):
        fget = obj.fget
        setattr(fget, "_is_indexed", True)
        return obj
    setattr(obj, "_is_indexed", True)
    return obj

class IndexNotifiable:
    """
    Если наш объект наследует от IndexNotifiable, то внутри у него:
     - self._caches  — set() «всех кэшей», в которых он сейчас лежит,
     - метод _register_cache(cache) — чтобы при put() в кэш объект зарегистрировал себя,
     - метод _notify_index_changed(field, old, new) — чтобы сеттер, изменив поле,
       послал всем этим кэшам сигнал «что-то у меня поменялось, поле field старое old, новое new».
    """
    def __init__(self):
        self._caches: set[CacheBase] = set()

    def _register_cache(self, cache):
        """
        Вызывается из cache.put(key, obj) один раз при вставке, чтобы «зарегистрировать связь»
        между этим объектом и данным кэшем. После этого, когда объект изменится, кэш знает,
        что ему нужно обновить индексы.
        """
        self._caches.add(cache)

    def _notify_index_changed(self, field_name, old_value, new_value):
        """
        Вызывается из сеттера/дескриптора, когда конкретное поле объекта поменялось.
        Пройдёмся по всем кэшам, где этот объект лежит, и «сигналим каждому»:
          «у меня поменялось поле field_name: старое old_value → новое new_value».
        """
        for cache in self._caches:
            cache._update_index_on_field_change(self, field_name, old_value, new_value)