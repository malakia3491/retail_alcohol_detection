from datetime import datetime
import re
from uuid import UUID
from Alc_Detection.Domain.Exceptions.Exceptions import InvalidCalibrationBoxes
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.Product import Product
from Alc_Detection.Domain.Store.Shelving import Shelving
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix

class Planogram:
    def __init__(self, 
                 shelving: Shelving,
                 product_matrix: ProductMatrix,
                 product_count: dict[Product, int],
                 author: Person,
                 create_date: datetime,
                 img_src: str=None,
                 id: UUID=None,
                 approver: Person=None,
                 approval_date: datetime=None):        
        self.id = id
        self.author = author
        self.shelving = shelving
        self.create_date = create_date
        self.product_matrix = product_matrix
        self.product_count = product_count 
        self.approver = approver
        self.approval_date = approval_date
        self.img_src = img_src
        self._order = None

    @property
    def planogram_order(self):
        return self._order
    
    @property
    def path(self) -> str:
        return self.img_src
    
    @planogram_order.setter
    def planogram_order(self, value):
        self._order = value
        
    def get_need_product_count(self, product: Product):
        return self.product_count[product]
    
    def approve(self,
                approver: Person,
                approval_date: datetime):
        self.approver = approver
        self.approval_date = approval_date
        
    def unapprove(self):
        self.approver = None
        self.approval_date = None
    
    def is_agreed(self):
        return not self.approver is None and not self.approval_date is None
    
    def set_calibrations(self, calibration_boxes: list[CalibrationBox]):
        try:
            self.product_matrix.calibrate(calibration_boxes)
        except ValueError:
            raise InvalidCalibrationBoxes(self.id) 
        
    def is_valid_calibrations(self, calibration_boxes: list[CalibrationBox]):
        return self.product_matrix.is_invalid_calibration(calibration_boxes)
     
    def copy(self):
        planogram = Planogram(shelving=self.shelving,
                              product_matrix=self.product_matrix.copy(),
                              product_count=self.product_count.copy(),
                              author=self.author,
                              create_date=self.create_date,
                              id=self.id,
                              approval_date=self.approval_date,
                              approver=self.approver)
        return planogram 
        
    def __eq__(self, value: 'Planogram'):
        return isinstance(value, Planogram) and \
               self.author == value.author and \
               self.shelving == value.shelving and \
               self.create_date == value.create_date and \
               self.product_count == value.product_count and \
               self.approver == value.approver and \
               self.approval_date == value.approval_date   
               
    def __hash__(self):
        hash_elements = [
            hash(self.author),  
            hash(self.shelving), 
            int(self.create_date.timestamp()) 
        ]
        if self.product_count:
            count_hash = hash(frozenset(
                (product.id, count) 
                for product, count in self.product_count.items()
            ))
            hash_elements.append(count_hash)
     
        if self.approver:
            hash_elements.append(hash(self.approver.id))
        if self.approval_date:
            hash_elements.append(int(self.approval_date.timestamp()))
        
        return hash(tuple(hash_elements))