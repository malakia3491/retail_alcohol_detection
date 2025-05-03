import sys
import os
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))
 
from Alc_Detection.API.app_ini import ModulesInitializer

async def async_main():
    app = FastAPI()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    IMAGES_PATH = os.path.join(
        BASE_DIR,
        "Alc_Detection",
        "Persistance",
        "Images",
        "ProductCrops"
    )

    app.mount(
        "/static/products",
        StaticFiles(directory=IMAGES_PATH),
        name="product_images"
    )
    
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