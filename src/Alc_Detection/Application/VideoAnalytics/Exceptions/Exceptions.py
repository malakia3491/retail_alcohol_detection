class ModelNotLoaded(Exception):
    def __init__(self, model_name: str, path_to_model: str):
        self.name = model_name
        self.path = path_to_model
        
    def __str__(self):
        return f"Model {self.name} by path {self.path} has been not loaded correctly!"
    
class NotCorrectImageFile(Exception):
    def __init__(self, file_name: str, mime_type: str, verify: bool):
        self.file_name = file_name
        self.mime_type = mime_type
        self.verify = verify
        
    def __str__(self):
        return f"Uploaded file {self.file_name} with MIME-type {self.mime_type} is not correct image file"