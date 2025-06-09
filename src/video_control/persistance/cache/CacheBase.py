import abc

class CacheBase(abc.ABC):
    @abc.abstractmethod
    def get(self, key):
        """
        Retrieves an item from the cache.

        Args:
            key (any): The key of the item to retrieve.

        Returns:
            any: The value associated with the key if found in the cache,
                 otherwise None.
        """
        pass
    @abc.abstractmethod  
    def get_by(self, field, value):
        """
        Получает объект по значению индексированного поля.
        
        Args:
            field (str): Имя индексированного поля.
            value (any): Значение, по которому ищем.

        Returns:
            any: Найденный объект или None.
        """
        pass
    
    @abc.abstractmethod
    def contains(self, value):
        pass
    
    @abc.abstractmethod
    def get_all(self):
        pass
    
    @abc.abstractmethod
    def put(self, key, value):
        """
        Adds an item to the cache.  If the cache is full, evicts the least recently used item.

        Args:
            key (any): The key of the item to add.
            value (any): The value associated with the key.
        """
        pass
    
    @abc.abstractmethod
    def __len__(self):
        """
        Returns the number of items currently in the cache.
        """
        pass
    
    @abc.abstractmethod
    def clear(self):
        """
        Clears all items from the cache.
        """
        pass
    
    @abc.abstractmethod
    def in_cache(self):
        pass
    
    @abc.abstractmethod
    def ids(self, *ids):
        pass
    
    @abc.abstractmethod
    def _update_index_on_field_change(self, obj, field_name, old_value, new_value):
        pass