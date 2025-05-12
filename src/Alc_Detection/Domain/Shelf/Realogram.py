from datetime import datetime

from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.EmptyDeviation import EmptyDeviation
from Alc_Detection.Domain.Shelf.DeviationManagment.IncongruityDeviation import incongruityDeviation
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Store.Shelving import Shelving
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductMatrix import ProductMatrix
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox

class Realogram:
    def __init__(self,
                 planogram: Planogram,
                 product_matrix: ProductMatrix, 
                 create_date: datetime,
                 img_src: str,
                 id=None):
        self.id = id
        self._create_date = create_date
        self._img_src = img_src
        self._product_matrix = product_matrix
        self._planogram = planogram 
        self._accordance = self._compute_accordance()
        self._compute_empties()
        
    @property
    def create_date(self) -> datetime:
        return self._create_date
    
    @property   
    def image_source(self) -> str:
        return self._img_src
    
    @property
    def image_url(self) -> str:
        return "/static/realograms/"+self._img_src
    
    @property
    def planogram(self) -> Planogram:
        return self._planogram

    @property
    def shelving(self) -> Shelving:
        return self._planogram.shelving
    
    @property
    def product_matrix(self) -> ProductMatrix:
        return self._product_matrix
    
    @property
    def empty_count(self) -> int:
        count = 0
        for _, shelf in self._product_matrix:
            for box in shelf.boxes:
                if box.is_empty: count+=1
        return count
        
    @property
    def accordance(self) -> float:
        return self._accordance
    
    def contains_deviation(self, deviation: Deviation):
        for realogram_dev in self.empties:
            if deviation.position == realogram_dev.position:
                return True
        for realogram_dev in self.inconsistencies:
            if deviation.position == realogram_dev.position:
                return True
        return False
    
    def _compute_accordance(self) -> float:
        r_matrix = self.product_matrix
        p_matrix = self.planogram.product_matrix
        accordance_count = 0
        deviations = []
        all_boxes_count = len(p_matrix)
        for (_, r_shelf), (_, p_shelf) in zip(r_matrix, p_matrix):
            r_boxes = r_shelf.boxes
            p_boxes = p_shelf.boxes
            for r_box, p_box in zip(r_boxes, p_boxes):
                if r_box.product == p_box.product:
                    if not r_box.is_empty:
                        accordance_count += 1
                else:
                    deviations.append(incongruityDeviation(
                        product_box=r_box,
                        right_product=p_box.product,
                    )) 
                    r_box.is_incorrect_position = True
        self._inconsistencies = deviations
        return accordance_count / all_boxes_count * 100
    
    def _compute_empties(self):
        deviations = []
        for _, shelf in self.product_matrix:
            for box in shelf.boxes:
                if box.is_empty:
                    deviations.append(EmptyDeviation(
                        product_box=box                                                
                    ))
        self._empties = deviations
    
    @property
    def empties(self) -> list[EmptyDeviation]:
        return self._empties
    
    @property
    def inconsistencies(self) -> list[incongruityDeviation]:
        return self._inconsistencies
    
    @property
    def deviation_count(self) -> int:
        return len(self.inconsistencies) + len(self.empties)