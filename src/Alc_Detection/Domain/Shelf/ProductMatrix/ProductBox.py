from Alc_Detection.Domain.Store.Product import Product
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point

class ProductBox:
    def __init__(
        self,
        id=None,
        product: Product=Product(),
        is_empty=False,
        is_incorrect_position = False
    ):
        from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.InitState import InitState
        self.set_state(InitState())
        self.id = id
        self._product = product
        self._is_empty = is_empty
        self._is_incorrect_position = is_incorrect_position
        
    def set_state(self, state) -> None:
        self._state = state
    
    def load_positions(self, point: Point) -> 'ProductBox':
        self._state.load_positions(self, point)
        return self
    
    def load_coordinates(self, xyxy: list, conf: float) -> 'ProductBox':
        if len(xyxy) != 4:
            raise ValueError(xyxy)
        self._state.load_coordinates(self, xyxy, conf)
        return self
        
    def load_positions_and_coordinates(self, xyxy: list, position: Point, conf: float) -> 'ProductBox':        
        self._state.load_positions_and_coordinates(self, xyxy, position, conf)
        return self
    
    @property
    def is_incorrect_position(self) -> bool:
        return self._is_incorrect_position
    
    @is_incorrect_position.setter
    def is_incorrect_position(self, value):
        self._is_incorrect_position = value 
    
    @property
    def product(self) -> Product:
        return self._product
    
    @product.setter
    def product(self, value):
        self._product = value   
    
    @property
    def is_empty(self) -> bool:
        return self._is_empty
    
    @is_empty.setter
    def is_empty(self, value: bool):
        self._is_empty = value
    
    @property
    def sort_point(self) -> Point:
        return self._state.sort_point(self)
    
    @property
    def position(self) -> Point:
        return self._state.position(self)
    
    @property
    def height(self) -> float:
        return self._state.height(self)
    
    @property
    def width(self) -> float:
        return self._state.width(self)
    
    @property
    def center(self) -> Point:
        return self._state.center(self)
    
    @property
    def width_point(self) -> Point:
        return self._state.width_point(self)
    
    @property
    def cords(self) -> list[int]:
        return self._state.cords(self)
    
    @property
    def p_min(self) -> Point:
        return self._state.p_min(self)
    
    @property
    def p_max(self) -> Point:
        return self._state.p_max(self)
    
    @property
    def conf(self) -> float:
        return self._state.conf(self)
    
    def copy(self) -> 'ProductBox':
        return self._state.copy(self)
    
    def is_same_position(self, other: 'ProductBox') -> bool:
        return self.position == other.position     
    
    def __eq__(self, other) -> bool:
        return self._state.eq(self, other)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:        
        return self._state.str(self)