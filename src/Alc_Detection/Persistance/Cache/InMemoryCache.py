from Alc_Detection.Persistance.Cache.CacheBase import CacheBase

class InMemoryCache(CacheBase):
    def __init__(self):
        self._cache = {}

    def get(self, key):
        """
        Retrieves an item from the _cache.

        Args:
            key (any): The key of the item to retrieve.

        Returns:
            any: The value associated with the key if found in the _cache,
                 otherwise None.
        """
        if key in self._cache:
            return self._cache[key]
        else: return None

    def get_all(self):
        return [obj for obj in self._cache.values()]

    def contains(self, value):
        if hasattr(value, "id") and not value.id is None:
            return self.get(value.id)
        else:            
            for obj in self.get_all():
                if obj == value: return obj
            return None
    
    def put(self, key, value):
        """
        Adds an item to the _cache.  If the _cache is full, evicts the least recently used item.

        Args:
            key (any): The key of the item to add.
            value (any): The value associated with the key.
        """
        self._cache[key] = value

    def clear(self):
        """
        Clears all items from the _cache.
        """
        self._cache = {}
        
    def __len__(self):
        """
        Returns the number of items currently in the _cache.
        """
        return len(self._cache)
    
    @property
    def ids(self):
        return self._cache.keys()
    
    def in_cache(self, *ids):
        not_in_ids = []
        in_ids = []
        for id in ids:
            if(id in self.ids): in_ids.append(id)
            else: not_in_ids.append(id) 
        return in_ids, not_in_ids