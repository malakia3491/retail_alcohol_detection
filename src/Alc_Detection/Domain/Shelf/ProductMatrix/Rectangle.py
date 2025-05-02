from typing import Optional

from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point

class Rectangle:
    def __init__(self, p1: Point, p2: Point):
        """Инициализирует прямоугольник по двум точкам (левый нижний и правый верхний углы)."""
        self.p_min = Point(min(p1.x, p2.x), min(p1.y, p2.y))
        self.p_max = Point(max(p1.x, p2.x), max(p1.y, p2.y))

    def __repr__(self) -> str:
        return f"Rectangle({self.p_min}, {self.p_max})"

    def __eq__(self, other: 'Rectangle') -> bool:
        return isinstance(other, Rectangle) and self.p_min == other.p_min and self.p_max == other.p_max
    
    def __str__(self) -> str:
        return f"Rectangle from {self.p_min} to {self.p_max}"

    def copy(self) -> 'Rectangle':
        return Rectangle(p1=self.p_min, p2=self.p_max)
    
    def width(self) -> float:
        """Возвращает ширину прямоугольника."""
        return self.p_max.x - self.p_min.x

    def height(self) -> float:
        """Возвращает высоту прямоугольника."""
        return self.p_max.y - self.p_min.y

    def area(self) -> float:
        """Возвращает площадь прямоугольника."""
        return self.width() * self.height()

    def perimeter(self) -> float:
        """Возвращает периметр прямоугольника."""
        return 2 * (self.width() + self.height())

    def center(self) -> Point:
        """Возвращает центр прямоугольника."""
        return Point(
            (self.p_min.x + self.p_max.x) / 2,
            (self.p_min.y + self.p_max.y) / 2
        )

    def contains_point(self, point: Point) -> bool:
        """Проверяет, содержится ли точка внутри прямоугольника (включая границы)."""
        return (
            self.p_min.x <= point.x <= self.p_max.x and
            self.p_min.y <= point.y <= self.p_max.y
        )

    def contains_rectangle(self, other: 'Rectangle') -> bool:
        """Проверяет, содержится ли другой прямоугольник полностью внутри текущего."""
        return (
            self.contains_point(other.p_min) and
            self.contains_point(other.p_max)
        )

    def intersects(self, other: 'Rectangle') -> bool:
        """Проверяет, пересекается ли прямоугольник с другим прямоугольником."""
        return not (
            self.p_max.x < other.p_min.x or
            self.p_min.x > other.p_max.x or
            self.p_max.y < other.p_min.y or
            self.p_min.y > other.p_max.y
        )

    def intersection(self, other: 'Rectangle') -> Optional['Rectangle']:
        """Возвращает прямоугольник пересечения или None, если пересечения нет."""
        if not self.intersects(other):
            return None

        new_p_min = Point(
            max(self.p_min.x, other.p_min.x),
            max(self.p_min.y, other.p_min.y)
        )
        new_p_max = Point(
            min(self.p_max.x, other.p_max.x),
            min(self.p_max.y, other.p_max.y)
        )

        return Rectangle(new_p_min, new_p_max)

    def union(self, other: 'Rectangle') -> 'Rectangle':
        """Возвращает минимальный прямоугольник, содержащий оба прямоугольника."""
        new_p_min = Point(
            min(self.p_min.x, other.p_min.x),
            min(self.p_min.y, other.p_min.y)
        )
        new_p_max = Point(
            max(self.p_max.x, other.p_max.x),
            max(self.p_max.y, other.p_max.y)
        )
        return Rectangle(new_p_min, new_p_max)

    def scale(self, factor: float) -> 'Rectangle':
        """Масштабирует прямоугольник относительно его центра."""
        center = self.center()
        new_width = self.width() * factor
        new_height = self.height() * factor
        half_width = new_width / 2
        half_height = new_height / 2

        new_p_min = Point(center.x - half_width, center.y - half_height)
        new_p_max = Point(center.x + half_width, center.y + half_height)

        return Rectangle(new_p_min, new_p_max)

    def move(self, dx: float = 0, dy: float = 0) -> 'Rectangle':
        """Сдвигает прямоугольник на dx и dy."""
        new_p_min = Point(self.p_min.x + dx, self.p_min.y + dy)
        new_p_max = Point(self.p_max.x + dx, self.p_max.y + dy)
        return Rectangle(new_p_min, new_p_max)