import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
import asyncio

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))
 
from Alc_Detection.API.app_ini import ModulesInitializer

async def async_main():
    app = FastAPI()

    starter = ModulesInitializer(app=app)
    await starter.initialize()
    
    config = uvicorn.Config(
        app, 
        host="127.0.0.1", 
        port=8000,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(async_main())