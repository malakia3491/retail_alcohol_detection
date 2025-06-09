class Store:
    def __init__(
        self,
        id: str,
        name: str, 
        address: str,
        code: str,
    ):
        self._id = id
        self._name = name
        self._address = address
        self._code = code
        
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def code(self) -> str:
        return self._code
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "code": self.code
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Store':
        return Store(
            id=data.get("id"),
            name=data.get("name"),
            address=data.get("address"),
            code=data.get("code")
        )
    
    def __str__(self) -> str:
        return f"Store(name={self.name}, address={self.address}"        
        
    def __repr__(self) -> str:
        return f"Store(id={self.id}, name={self.name}, address={self.address}, code={self.code})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Store):
            return False
        return (
            self.name == other.name and
            self.address == other.address and
            self.code == other.code
        )        
        
    def __hash__(self) -> int:
        return hash((self.name, self.address, self.code))