from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.CompleteState import CompleteState
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.PositionsLoadedState import PositionsLoadedState
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.CoordinatesLoadedState import CoordinatesLoadedState
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.ProductBoxState import ProductBoxState
from Alc_Detection.Domain.Shelf.ProductMatrix.Rectangle import Rectangle
from Alc_Detection.Domain.Exceptions.Exceptions import *

class InitState(ProductBoxState):
    def load_positions(self, product_box: ProductBox, position: Point) -> None:        
        product_box.set_state(PositionsLoadedState())
        product_box._position = position

    def load_coordinates(self, product_box: ProductBox, xyxy: list, conf: float) -> None:
        product_box.set_state(CoordinatesLoadedState())
        product_box._rectangle = Rectangle(Point(xyxy[0], xyxy[1]), Point(xyxy[2], xyxy[3]))
        product_box._conf = conf
        
    def load_positions_and_coordinates(self, product_box: ProductBox, xyxy: list, position: Point, conf: float) -> None:
        product_box.set_state(CompleteState())
        product_box._rectangle = Rectangle(Point(xyxy[0], xyxy[1]), Point(xyxy[2], xyxy[3]))
        product_box._position = position
        product_box._conf = conf
        
    def sort_point(self, product_box: ProductBox):
        raise PositionsNotLoaded()
    
    def position(self, product_box: ProductBox):
        raise PositionsNotLoaded() 
    
    def height(self, product_box: ProductBox):
        raise CoordinatesNotLoaded()
    
    def width(self, product_box: ProductBox):
        raise CoordinatesNotLoaded()
    
    def width_point(self, product_box: ProductBox):
        raise CoordinatesNotLoaded()
    
    def center(self, product_box: ProductBox):
        raise CoordinatesNotLoaded()
    
    def p_min(self):
        raise CoordinatesNotLoaded()
    
    def p_max(self):
        raise CoordinatesNotLoaded()
    
    def conf(self, product_box: ProductBox):
        raise CoordinatesNotLoaded()
    
    def copy(self, product_box: ProductBox):
        return ProductBox(product=product_box.product.copy(),
                          is_empty=product_box.is_empty)
    
    def eq(self, product_box: ProductBox, other) -> bool:
        return isinstance(other, ProductBox) and \
               isinstance(other._state, InitState) and \
               product_box.product == other.product and \
               product_box.is_empty == other.is_empty
    
    def str(self, product_box: ProductBox) -> str:        
        string = f'EmptyBox' if product_box.is_empty else f'[{product_box.product.name}]'
        return string