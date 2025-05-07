from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.CompleteState import CompleteState
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.ProductBoxState import ProductBoxState
from Alc_Detection.Domain.Shelf.ProductMatrix.Rectangle import Rectangle
from Alc_Detection.Domain.Exceptions.Exceptions import *

class PositionsLoadedState(ProductBoxState):
    def load_positions(self, product_box: ProductBox, position: Point) -> None:
        product_box._position = position
    
    def load_coordinates(self, product_box: ProductBox, xyxy: list, conf: float) -> None:
        product_box.set_state(CompleteState())
        product_box._rectangle = Rectangle(Point(xyxy[0], xyxy[1]), Point(xyxy[2], xyxy[3]))
        product_box._conf = conf
        
    def load_positions_and_coordinates(self, product_box: ProductBox, xyxy: list, position: Point, conf: float) -> None:
        product_box.set_state(CompleteState())
        product_box._rectangle = Rectangle(Point(xyxy[0], xyxy[1]), Point(xyxy[2], xyxy[3]))
        product_box._conf = conf
        
    
    def sort_point(self, product_box: ProductBox):
        return product_box._position
    
    def position(self, product_box: ProductBox):
        return product_box._position
    
    def height(self, product_box: ProductBox):
        return None
       
    def width(self, product_box: ProductBox):
        return None
    
    def center(self, product_box: ProductBox):
        return None
    
    def width_point(self, product_box: ProductBox):
        return None
    
    def p_min(self, product_box: ProductBox):
        return None
    
    def p_max(self, product_box: ProductBox):
        return None

    def cords(self, product_box: ProductBox):
        return None
    
    def conf(self, product_box: ProductBox):
        return None
    
    def copy(self, product_box: ProductBox):
        new_p_box = ProductBox(product=product_box.product.copy(),
                               is_empty=product_box.is_empty)

        new_p_box.load_positions(product_box.position)        
        return new_p_box
    
    def eq(self, product_box: ProductBox, other) -> bool:
        return isinstance(other, ProductBox) and \
               isinstance(other._state, PositionsLoadedState) and \
               product_box.product == other.product and \
               product_box.is_empty == other.is_empty and \
               product_box.position == other.position
    
    def str(self, product_box: ProductBox) -> str:        
        string = f'EmptyBox({product_box.position}))' if product_box.is_empty else f'[{product_box.product.name}]({product_box.position})'
        return string