from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from ..db_conn import DbDependencyServer
from ..models.images import Image

from uuid import UUID, uuid4
from typing import BinaryIO, Annotated
from ..validator.validate import call_validate_func_on_data

image_router = APIRouter()
images_collection_name = "IMAGES_COLLECTION"
db_dep = DbDependencyServer("images_logger", "/var/images_logger.log")
DatabaseDep = Annotated[DbDependencyServer, Depends(db_dep)]

@image_router.get("/image/")
def get_image(
            db_dep : DatabaseDep,
            user_id: str = Query(None, title="User id"), 
            position : int = Query(None, title="Which image"),
        ) -> Image:

    image_query = {'_id': user_id, 'position': position}
    get_img = db_dep.get_collection_document(images_collection_name, image_query)
    return { "user_id": get_img["_id"], "position": get_img["position"], "binary": get_img["binary"]}

@image_router.post("/image/")
def post_image(
            db_dep : DatabaseDep,
            image: Image
        ) -> JSONResponse:

    image_post = { "_id": uuid4(), "position": image.position, "binary": image.binary }  
    result = db_dep.post_collection_document(images_collection_name, image_post)
    if call_validate_func_on_data(data=str(result.inserted_id), validate_func=UUID, app_logger=db_dep.app_logger):
        return JSONResponse(content="Successfully added document to collection", status_code=200)
    return JSONResponse(content="Adding document to collection failed. Check image API logs", status_code=404)
