class Shelving:
    def __init__(
        self,
        id: str,
        name: str,
    ):
        self._id = id
        self._name = name

    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name  

    def __eq__(self, value):
        if not isinstance(value, Shelving):
            return False
        return self.name == value.name
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"Shelving(name={self.name})"

    def __repr__(self):
        return f"Shelving(id={self.id}, name={self._name})"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }