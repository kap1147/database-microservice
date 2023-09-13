import os

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .routes.images import image_router as ImageRouter
from .bootstrahpper.bootstrapper import *

def main():
    load_dotenv()
    app = FastAPI()

    origins = [
        os.getenv("RAH_TH_SIGHT"),  # Allow local development access
    ]

    #Restrict in PRD
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(ImageRouter)
    return app


if __name__ == "__main__":
    main()
