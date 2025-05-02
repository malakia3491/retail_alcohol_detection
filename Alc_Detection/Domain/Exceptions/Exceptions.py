class CoordinatesNotLoaded(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return ""
    
class PositionsNotLoaded(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return ""
    
class InvalidStateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
    
class InvalidCalibrationBoxes(Exception):
    def __init__(self, planogram_id):
        self.planogram_id = planogram_id
        
    def __str__(self):
        return f"Invalid colibration boxes for calibrate planogram with id {self.planogram_id}"
    
class ApprovePlanogramInDeclinedOrder(Exception):
    def __init__(self, order_id):
        self.planogram_id = order_id
        
    def __str__(self):
        return f"You can`t approve planogram in declined order with id {self.planogram_id}"
    
class ImageError(Exception):
    def __init__(self, path):
        self.path = path
        
    def __str__(self):
        return f"Изображение по пути {self.path} не может быть использовано!"