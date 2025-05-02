from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from Alc_Detection.Persistance.Interfaces.Interfaces import ConfigReader
from Alc_Detection.Persistance.Models.BaseModel import BaseModel
from Alc_Detection.Persistance.Models.Models import *


class DbInitializer:
    def __init__(self, config_reader: ConfigReader):
        self.config_reader = config_reader
    
    async def initialize(self):
        sql_connection = self.config_reader.get_db_connection()
        engine = create_async_engine(sql_connection, echo=False)
                
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        
        AsyncSessionLocalFabric = sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False)        
        return AsyncSessionLocalFabric