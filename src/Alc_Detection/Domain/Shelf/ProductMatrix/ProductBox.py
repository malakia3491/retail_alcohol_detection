from Alc_Detection.Domain.Store.Product import Product
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point

class ProductBox:
    def __init__(self, id=None, product: Product=Product(), is_empty=False):
        from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.InitState import InitState
        self.set_state(InitState())
        self.id = id
        self._product = product
        self._is_empty = is_empty
        self._is_incorrect_position = False
        
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
    def is_incorrect_position(self):
        return self._is_incorrect_position
    
    @is_incorrect_position.setter
    def is_incorrect_position(self, value):
        self._is_incorrect_position = value 
    
    @property
    def product(self):
        return self._product
    
    @product.setter
    def product(self, value):
        self._product = value   
    
    @property
    def is_empty(self):
        return self._is_empty
    
    @is_empty.setter
    def is_empty(self, value: bool):
        self._is_empty = value
    
    @property
    def sort_point(self):
        return self._state.sort_point(self)
    
    @property
    def position(self):
        return self._state.position(self)
    
    @property
    def height(self):
        return self._state.height(self)
    
    @property
    def width(self):
        return self._state.width(self)
    
    @property
    def center(self):
        return self._state.center(self)
    
    @property
    def width_point(self):
        return self._state.width_point(self)
    
    @property
    def p_min(self):
        return self._state.p_min(self)
    
    @property
    def p_max(self):
        return self._state.p_max(self)
    
    @property
    def conf(self):
        return self._state.conf(self)
    
    def copy(self):
        return self._state.copy(self)
    
    def __eq__(self, other) -> bool:
        return self._state.eq(self, other)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:        
        return self._state.str(self)