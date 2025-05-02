import abc

from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox

class ProductBoxState(abc.ABC):    
    @abc.abstractmethod
    def load_positions(self, product_box: ProductBox, position: Point) -> None:
        pass
    
    @abc.abstractmethod
    def load_coordinates(self, product_box: ProductBox, xyxy: list) -> None:
        pass

    @abc.abstractmethod
    def load_positions_and_coordinates(self, product_box: ProductBox, xyxy: list, position: Point, conf: float) -> None:
        pass
    
    @abc.abstractmethod
    def sort_point(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def position(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def height(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def width(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def center(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def width_point(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def p_min(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def p_max(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def conf(self, product_box: ProductBox):
        pass
    
    @abc.abstractmethod
    def copy(self,  product_box: ProductBox) -> ProductBox:
        pass
    
    @abc.abstractmethod
    def eq(self, product_box: ProductBox, other) -> bool:
        pass
    
    @abc.abstractmethod
    def str(self, product_box: ProductBox) -> str:        
        pass