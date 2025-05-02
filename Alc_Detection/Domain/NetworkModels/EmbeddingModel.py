class EmbeddingNetwork:
    def __init__(self, path: str, embedding_shape=256, version: str="", id=None):
        self.id = id
        self._path = path
        self._version = version
        self._embedding_shape = embedding_shape

    @property        
    def path(self) -> str:
        return self._path
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def embedding_shape(self) -> int:
        return self._embedding_shape
    
    def __eq__(self, value) -> bool:
        return isinstance(value, EmbeddingNetwork) and \
               self._path == value.path
               
    def __hash__(self):
        return hash(self._path)
    
    def __str__(self):
        return f"Path({self._path}) Version({self._version})"