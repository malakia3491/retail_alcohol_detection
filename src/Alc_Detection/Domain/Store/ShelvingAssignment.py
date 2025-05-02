from Alc_Detection.Domain.Store.PlanogramOrder import PlanogramOrder
from Alc_Detection.Domain.Store.Shelving import Shelving

class ShelvingAssignment:
    def __init__(self, shelving: Shelving, planogram_order: PlanogramOrder):
        self.shelving = shelving
        self.planogram_order = planogram_order