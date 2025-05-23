from typing import Dict, List, Tuple, Union
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.InitState import InitState
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBoxStates.PositionsLoadedState import PositionsLoadedState
from Alc_Detection.Domain.Shelf.ProductMatrix.Rectangle import Rectangle
from Alc_Detection.Domain.Store.Product import Product

class Shelf:
    """Класс, инкапсулирующий полку со списком ProductBox и связанную с ней геометрию"""
    def __init__(self, boxes: List[ProductBox], is_empty: bool = False):
        self._boxes: List[ProductBox] = self.sort_boxes(boxes)
        if is_empty:
            for box in self._boxes:
                box.is_empty = True                       
        self.update_rectangle()
        
    @property
    def boxes(self):
        return self.sort_boxes(self._boxes)

    def is_no_rectangle(self):
        if self.is_empty or not hasattr(self, "_boxes") or len(self._boxes) == 0:
            return True
        if not hasattr(self._boxes[0], "_state"):
            return True        
        try:
            box_state = self._boxes[0]._state  
        except AttributeError:
            return True  

        return isinstance(box_state, (PositionsLoadedState, InitState))
    
    def _compute_rectangle(self) -> Rectangle:
        if not self._boxes:
            raise ValueError("Невозможно вычислить Rectangle для пустой полки")
        p_min = self._boxes[0].p_min
        p_max = self._boxes[-1].p_max
        return Rectangle(p_min, p_max)

    def set_products(self, products: list[Product]):
        if len(self) != len(products):
            raise ValueError(products)
        for product, box in zip(products, self._boxes):
            box.product = product
    
    def add_product(self, box: ProductBox) -> None:
        self._boxes.append(box.copy())
        self._boxes = self.sort_boxes(self._boxes)
        self.update_rectangle()
    
    def set_boxes(self, _boxes: List[ProductBox]) -> None:
        self._boxes = self.sort_boxes(_boxes.copy())
        self.update_rectangle()
    
    def update_rectangle(self) -> None:
        if not self.is_no_rectangle():            
            self.rectangle = self._compute_rectangle()

    def __len__(self) -> int:
        return len(self._boxes)

    @property
    def is_empty(self) -> bool:
        return self._boxes is None or len(self._boxes) == 0 or all(box.is_empty for box in self._boxes)

    def __eq__(self, other: 'Shelf') -> bool:
        if len(self._boxes) != len(other._boxes):
            return False
        return all(b1 == b2 for b1, b2 in zip(self._boxes, other._boxes))

    def get_box_index(self, box: ProductBox) -> int:
        if box not in self._boxes:
            raise ValueError(f"Коробка не найдена на полке: {box}")
        return self._boxes.index(box)

    def get_boxes_between(
        self,
        x1: float,
        x2: float,
        margin: float = 5
    ) -> List[ProductBox]:
        result: List[ProductBox] = []
        for box in self._boxes:
            coord = box.center.x
            if x1 < coord - margin and coord + margin < x2:
                result.append(box.copy())
        return result

    def insert_boxes(self, new_boxes: List[ProductBox], position: int) -> None:
        if position < 0 or position > len(self._boxes):
            raise IndexError(f"Недопустимая позиция вставки: {position}")
        self._boxes = self._boxes[:position] + new_boxes + self._boxes[position:]
        self.update_rectangle()
        self._update_positions()

    def _update_positions(self):
        for position_y, box in enumerate(self._boxes):
            box.load_positions(point=Point(box.position.x, position_y))

    def sort_boxes(self, _boxes) -> List[ProductBox]:
        return sorted(_boxes, key=lambda p: p.sort_point)

    @property
    def width(self) -> float:
        if not self.is_no_rectangle(): 
            return self.rectangle.width()
        return None

    @property
    def height(self) -> float:
        if not self.is_no_rectangle(): 
            return self.rectangle.height()
        return None
    
    @property
    def center(self) -> float:
        if not self.is_no_rectangle(): 
            return self.rectangle.center()
        return None
    @property
    def height_point(self) -> Point:
        if not self.is_no_rectangle(): 
            return Point(self.rectangle.p_min.y, self.rectangle.p_max.y)
        return None

    def __repr__(self) -> str:
        return f"Shelf(_boxes={self._boxes})"