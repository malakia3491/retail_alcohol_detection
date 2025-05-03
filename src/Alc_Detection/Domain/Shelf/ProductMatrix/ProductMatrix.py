from typing import Union
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox
from Alc_Detection.Domain.Shelf.ProductMatrix.Shelf import Shelf
from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox

class ProductMatrix:
    """Класс для управления матрицей стеллажей с продуктами"""
    def __init__(
        self,
        shelving_count = None,
        shelves: dict[int, Shelf] = None,
        is_empty: bool = False
    ):
        self._shelves: dict[int, Shelf] = {}
        if not shelving_count is None:
            for idx in range(0, shelving_count):
                self._shelves[idx] = Shelf(boxes=[])
        if not shelves is None:
            for idx in shelves:
                self._shelves[idx] = shelves[idx]
        self._rows = len(self._shelves)
        if is_empty:
            for shelf in self._shelves.values():
                for box in shelf.boxes:
                    box.is_empty = True
        
    def fill(self, shelves: dict[int, Shelf]) -> None:
        if len(shelves) != self._rows:
            raise ValueError("Количество переданных полок не соответствует заданному числу рядов")
        self._shelves = {idx: shelf for idx, shelf in shelves.items()}

    def define_positions(self) -> 'ProductMatrix':
        for row_id, shelf in self:
            for column_id, box in enumerate(shelf.boxes):
                box.load_positions(Point(row_id, column_id))
        return self
    
    @property
    def len_shelves(self) -> int:
        return len(self._shelves)

    @property
    def shape(self) -> list[int]:
        return [len(shelf) for shelf in self._shelves.values()]

    @property
    def is_empty(self) -> bool:
        return all(shelf.is_empty for shelf in self._shelves.values())

    @is_empty.setter
    def is_empty(self, value: bool) -> None:
        for shelf in self._shelves.values():
            for box in shelf.boxes:
                box.is_empty = value
    
    def add_product(self, product: ProductBox) -> bool:
        row, col = product.position.x, product.position.y
        if row not in self._shelves or col < 0:
            raise ValueError(f"Неверные координаты: ({row}, {col})")
        self._shelves[row].add_product(product)
        return True

    def add_products(self, products: list[ProductBox]) -> bool:
        return all(self.add_product(p) for p in products)

    def is_invalid_calibration(self, boxes: list[CalibrationBox]):
        if len(boxes) != len(self):
            raise ValueError((len(self), len(boxes)))
        matrix_boxes: list[ProductBox] = []
        [matrix_boxes.extend(self._shelves[shelf].boxes) for shelf in self._shelves]
        boxes = sorted(boxes, key=lambda box: box.matrix_cords)
        matrix_boxes = sorted(matrix_boxes, key=lambda box: box.position)
        return all(box1.matrix_cords == box2.position for box1, box2 in zip(boxes, matrix_boxes))
    
    def calibrate(self, boxes: list[CalibrationBox]):
        if len(boxes) != len(self):
            raise ValueError(boxes) 
        for _, shelf in self._shelves.items():
            for box in shelf.boxes:
                is_calibrated = False   
                for c_box in boxes:
                    if c_box.is_same_pos(box.position):
                        box.load_coordinates(xyxy=c_box.xyxy, conf=c_box.conf)
                        is_calibrated = True
                if not is_calibrated: 
                    raise ValueError(boxes)
    
    def add_products_with_coords(
        self,
        product_shelves: list[list[ProductBox]]
    ) -> bool:
        sorted_shelves = sorted(
            product_shelves,
            key=lambda shelf: Shelf(shelf).center()
        )
        for s_index, shelf_boxes in enumerate(sorted_shelves):
            shelf_obj = Shelf(shelf_boxes)
            sorted_boxes = shelf_obj.sort_boxes()
            for p_index, box in enumerate(sorted_boxes):
                box.load_positions(Point(s_index, p_index))
                self.add_product(box)
        return True

    def insert_shelves(
        self,
        new_shelves: dict[int, Shelf],
        bounds: tuple[int, int]
    ) -> None:
        left, right = bounds
        if left < -1 or right > self.len_shelves:
            raise IndexError("Индексы границ выходят за диапазон")

        first = {k: v for k, v in self._shelves.items() if k <= left}
        last = {k: v for k, v in self._shelves.items() if k > right}

        new_matrix: dict[int, Shelf] = {}
        idx = 0
        for k in sorted(first):
            new_matrix[idx] = first[k]
            idx += 1
        for new in new_shelves.values():
            new_matrix[idx] = new
            idx += 1
        for k in sorted(last):
            new_matrix[idx] = last[k]
            idx += 1
        self._shelves = new_matrix
        self._rows = len(self._shelves)

    def get_shelf_index(self, shelf: Shelf) -> int:
        for idx, s in self._shelves.items():
            if s.equals(shelf):
                return idx
        raise ValueError(f"Полка не найдена: {shelf}")

    def __getitem__(
        self,
        key: int
    ) -> Shelf:
        if key not in self._shelves:
            raise IndexError("Полка с таким индексом не существует")
        return self._shelves[key]

    def copy(self) -> 'ProductMatrix':
        copied = {idx: Shelf([box.copy() for box in shelf.boxes], is_empty=shelf.is_empty) for idx, shelf in self._shelves.items()}
        return ProductMatrix(shelves=copied)

    def __iter__(self):
        for id, shelf in self._shelves.items():
            yield id, shelf

    def __repr__(self) -> str:
        if self.is_empty:
            return "EmptyProductMatrix"
        lines = []
        for idx, shelf in self._shelves.items():
            lines.append(f"=== Полка {idx} ===")
            lines.append(" | ".join(str(box) for box in shelf.boxes))
        return "\n".join(lines)
    
    def __len__(self):
        return sum(self.shape)

    def __eq__(self, value: 'ProductMatrix'):
        return isinstance(value, ProductMatrix) and \
               self.len_shelves == value.len_shelves and \
               all(self._shelves[shelf1] == value._shelves[shelf2] for shelf1, shelf2 in zip(self._shelves, value._shelves))