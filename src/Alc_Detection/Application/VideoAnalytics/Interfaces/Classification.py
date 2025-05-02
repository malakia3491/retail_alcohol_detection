import abc

from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix

class ClassificationService(abc.ABC):
    @abc.abstractmethod
    def classificate(self, product_matrix: ProductMatrix) -> ProductMatrix:
        pass