from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.Rectangle import Rectangle

class CalibrationBox:
    def __init__(self, xyxy: list[int], matrix_cords: list[int], conf: float):
        if len(xyxy) != 4:
            raise ValueError(xyxy)
        if len(matrix_cords) != 2:
            raise ValueError(matrix_cords)
        if conf is None:
            raise ValueError(conf)
        self._rectangle = Rectangle(Point(xyxy[0], xyxy[1]), Point(xyxy[2], xyxy[3]))
        self._xyxy = xyxy.copy()
        self._matrix_cords = Point(x=matrix_cords[0], y=matrix_cords[1])
        self._conf = conf

    @property        
    def rectangle(self):
        return self._rectangle.copy()
    
    @property
    def xyxy(self):
        return self._xyxy
    
    @property
    def matrix_cords(self):
        return self._matrix_cords.copy()
    
    @property
    def conf(self):
        return self._conf
    
    def is_same_pos(self, matrix_pos: Point):
        return self.matrix_cords == matrix_pos
    
    def __str__(self):
        return f"({self.matrix_cords.x}, {self.matrix_cords.y})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, value):
        return isinstance(value, CalibrationBox) and \
               self.xyxy == value.xyxy and \
               self.matrix_cords == value.matrix_cords and \
               self.conf == value.conf
               
    def __hash__(self):
        return hash((self.xyxy, self.matrix_cords, self.conf))