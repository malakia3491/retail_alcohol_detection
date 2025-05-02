import math

class Point:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def copy(self) -> 'Point':
        return Point(x=self.x, y=self.y)
    
    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: 'Point') -> bool:
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __add__(self, other: 'Point') -> 'Point':
        if not isinstance(other, Point):
            raise TypeError("Operands must be of type Point")
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        if not isinstance(other, Point):
            raise TypeError("Operands must be of type Point")
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Point':
        if not isinstance(scalar, (int, float)):
            raise TypeError("Scalar must be a number")
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Point':
        if not isinstance(scalar, (int, float)):
            raise TypeError("Scalar must be a number")
        if scalar == 0:
            raise ValueError("Division by zero is not allowed")
        return Point(self.x / scalar, self.y / scalar)

    def distance_to(self, other: 'Point') -> float:
        """Вычисляет евклидово расстояние между двумя точками."""
        if not isinstance(other, Point):
            raise TypeError("Operand must be of type Point")
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def magnitude(self) -> float:
        """Возвращает расстояние от начала координат (0, 0) до точки."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def to_tuple(self) -> tuple[float, float]:
        """Возвращает координаты точки в виде кортежа (x, y)."""
        return (self.x, self.y)

    def to_list(self) -> list[float, float]:
        return [self.x, self.y]

    def move(self, dx: float = 0, dy: float = 0) -> 'Point':
        """Сдвигает точку на dx и dy. Возвращает новую точку."""
        return Point(self.x + dx, self.y + dy)
    
    def __lt__(self, other: 'Point') -> bool:
        """Определяет порядок точек по координате x (и y если x одинаковые)."""
        if not isinstance(other, Point):
            raise TypeError("Operand must be of type Point")
        if self.x < other.x:
            return True
        elif self.x > other.x:
            return False
        else:  # x values are equal, compare y values
            return self.y < other.y