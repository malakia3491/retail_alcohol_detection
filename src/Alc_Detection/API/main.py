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
    )

    app.mount(
        "/static/planograms",
        StaticFiles(directory=os.path.join(IMAGES_PATH, "Planograms")),
        name="planograms"
    )

    app.mount(
        "/static/realograms",
        StaticFiles(directory=os.path.join(IMAGES_PATH, "Realograms")),
        name="realograms_snapshots"
    )

    app.mount(
        "/static/products",
        StaticFiles(directory=os.path.join(IMAGES_PATH, "ProductCrops")),
        name="product_images"
    )
    
    starter = ModulesInitializer(app=app)
    await starter.initialize()
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=8000,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(async_main())