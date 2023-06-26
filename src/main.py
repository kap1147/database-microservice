from fastapi import FastAPI
from .routes.images import image_router as ImageRouter

app = FastAPI()
app.include_router(ImageRouter)



