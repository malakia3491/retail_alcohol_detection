class Config:
    def __init__(
        self,
        id: str=None,
        address: str=None,
        name: str=None,
        login: str=None,
        password: str=None,
        code: str=None,
    ):
        self.id = id
        self.address = address
        self.name = name
        self.login = login
        self.password = password
        self.code = code
                
    @property
    def is_filled(self) -> bool:
        return bool(self.login and self.password and self.code)    

    @property 
    def is_stored_data(self) -> bool:
        """
        Check if the configuration contains stored data.
        
        :return: True if all fields are filled, False otherwise.
        """
        return bool(self.id and self.name and self.login and self.password and self.code)    
        
    def from_dict(self, **args):
        """
        Create a Confing instance from a dictionary.
        
        :param args: Dictionary containing configuration parameters.
        :return: Confing instance.
        """
        return Config(
            id=args.get('id', ''),
            address=args.get('address', ''),
            name=args.get('name', ''),
            login=args.get('login', ''),
            password=args.get('password', ''),
            code=args.get('code', '')
        )