from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.ProductBoxState import ProductBoxState
from Alc_Detection.Domain.Exceptions.Exceptions import *

class CompleteState(ProductBoxState):
    def load_positions(self, product_box: ProductBox, position: Point) -> None:
        raise InvalidStateError("Позиции уже загружены!")
    
    def load_coordinates(self, product_box: ProductBox, xyxy: list, conf: float) -> None:
        raise InvalidStateError("Координаты уже загружены!")
    
    def load_positions_and_coordinates(self, product_box: ProductBox, xyxy: list, position: Point, conf: float) -> None:
        raise InvalidStateError("Планограмма завершена!")
        
    
    def sort_point(self, product_box: ProductBox):
        return product_box._position
    
    
    def position(self, product_box: ProductBox):
        return product_box._position
    
    
    def height(self, product_box: ProductBox):
        return product_box._rectangle.height()
    
    
    def width(self, product_box: ProductBox):
        return product_box._rectangle.width()
    
    
    def center(self, product_box: ProductBox):
        return product_box._rectangle.center()
    
    
    def width_point(self, product_box: ProductBox):
        return Point(product_box._rectangle.p_min.x, product_box._rectangle.p_max.x)
    
    def p_min(self, product_box: ProductBox):
        return product_box._rectangle.p_min
    
    def p_max(self, product_box: ProductBox):
        return product_box._rectangle.p_max
    
    def conf(self, product_box: ProductBox):
        return product_box._conf
    
    def copy(self, product_box: ProductBox):
        new_p_box = ProductBox(product=product_box.product.copy(),
                          is_empty=product_box.is_empty)
        xyxy = [product_box._rectangle.p_min.x,
                product_box._rectangle.p_min.y,
                product_box._rectangle.p_max.x,
                product_box._rectangle.p_max.y]
        new_p_box.load_positions_and_coordinates(xyxy=xyxy,
                                                 position=product_box.position,
                                                 conf=product_box.conf)        
        return new_p_box
    
    def eq(self, product_box: ProductBox, other) -> bool:
        return isinstance(other, ProductBox) and \
               isinstance(other._state, CompleteState) and \
               product_box.product == other.product and \
               product_box.is_empty == other.is_empty and \
               product_box._rectangle == other._rectangle and \
               product_box.position == other.position
    
    def str(self, product_box: ProductBox) -> str:        
        string = f'EmptyBox' if product_box.is_empty else f'[{product_box.product.name}]({product_box.position})'
        return string