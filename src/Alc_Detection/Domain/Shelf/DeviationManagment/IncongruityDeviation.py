from datetime import time

from Alc_Detection.Domain.Store.Person import Person
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation

class incongruityDeviation(Deviation):
    def __init__(
        self,
        product_box: ProductBox,
        responsible_employees: list[Person],
        elimination_time: time=None,
    ):
        super().__init__(
            product_box=product_box,
            elimination_time=elimination_time,
            responsible_employees=responsible_employees
        )