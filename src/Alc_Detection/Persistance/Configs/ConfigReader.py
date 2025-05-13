import configparser
from pathlib import Path

from Alc_Detection.Persistance.Interfaces.Interfaces import ConfigReader 

class IniConfigReader(ConfigReader):
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.config = configparser.ConfigParser()
            
    def get_db_connection(self, is_async=True):
        try:
            self.config.read(self.path_to_config)
            str_connection = self.config["Database"]["ASYNC_SQLALCHEMY_DATABASE_URL"] if is_async else self.config["Database"]["SQLALCHEMY_DATABASE_URL"]
            return str_connection
        except Exception as ex:
            raise ex
        
    def get_secret(self) -> str:
        try:
            self.config.read(self.path_to_config)
            secret = self.config["AUTH"]["SECRET_KEY"]
            return secret
        except Exception as ex:
            raise ex

    def get_algorithm(self) -> str:
        try:
            self.config.read(self.path_to_config)
            algorithm = self.config["AUTH"]["ALGORITHM"]
            return algorithm
        except Exception as ex:
            raise ex
        
    def get_access_token_expire(self) -> int:
        try:
            self.config.read(self.path_to_config)
            expire = int(self.config["AUTH"]["ACCESS_TOKEN_EXPIRE_MINUTES"])
            return expire
        except Exception as ex:
            raise ex
    
    def get_model_path(self,
                       model_type: str,
                       version: str
    ) -> str:
        try:
            self.config.read(self.path_to_config)
            base_path = self.config["models"]["BASE_PATH"]
            path = base_path + self.config[model_type][version]
            return Path(path)
        except Exception as ex:
            raise ex
        
    def get_save_dir_path(self,
                          type_str: str
    ) -> str:
        try:
            self.config.read(self.path_to_config)
            path = self.config["img_save_dirs"][type_str]
            return Path(path)
        except Exception as ex:
            raise ex
        
    def get_tg_api_key(self) -> str:
        try:
            self.config.read(self.path_to_config)
            token = self.config["Telegram"]["API_TOKEN"]
            return token 
        except Exception as ex:
            raise ex

    def get_retail_api_base_url(self) -> str:
        try:
            self.config.read(self.path_to_config)
            url_path = self.config["RetailAPI"]["BASE_URL"]
            return url_path 
        except Exception as ex:
            raise ex        
        
    def get_webhook_url(self) -> str:
        try:
            self.config.read(self.path_to_config)
            url_path = self.config["Telegram"]["WEBHOOK_URL"]
            return url_path 
        except Exception as ex:
            raise ex