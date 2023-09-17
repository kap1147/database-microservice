from uuid import UUID, uuid4
from typing import Annotated
from io import BytesIO

from fastapi import APIRouter, Depends, Query, FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from ..db_conn import DbDependencyServer
from ..models.images import ImagePost, ImageGet
from ..pillow.image_setter import pillow_image_setter
from ..validator.validate import call_validate_func_on_data

image_router = APIRouter()
images_database_name = "IMAGES_DB"
images_collection_name = "IMAGES_COLLECTION"
db_dep = DbDependencyServer(images_database_name ,images_collection_name, "images_logger", "/var/opt/user_images/images_logger.log")
DatabaseDep = Annotated[DbDependencyServer, Depends(db_dep)]

@image_router.get("/image/")
def get_image(
            db_dep : DatabaseDep,
            user_id: str = Query(None, title="User id"), 
            system_name: str = Query(None, title="System name"), 
            prop_type: str = Query(None, title="Object property tyep"),
            position : int = Query(None, title="Which image"),
        ):
    try:
        ImageGet(
            user_id=UUID(user_id),
            system_name=str(system_name),
            prop_type=str(prop_type),
            position=int(position)
        )
    except TypeError as e:
        raise HTTPException(status_code=422, detail=str(e))

    image_query = {"user_id": UUID(user_id), "system_name": system_name, "position": position, "prop_type": prop_type}
    get_img = db_dep.get_collection_document(images_collection_name, image_query)

    if get_img:
        return StreamingResponse(BytesIO(getattr(get_img, "binary")), media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Item not found")

@image_router.post("/image/")
def post_image(
            db_dep : DatabaseDep,
            image: ImagePost
        ) -> JSONResponse:
    
    try:
        img = pillow_image_setter(image.filename, db_dep.app_logger)
    except Exception as e:
        msg = f"Issue loading image. Check image API logs:\n{e}"
        db_dep.app_logger.error(msg)
        return JSONResponse(content=msg, status_code=400)

    image_post = { "_id": uuid4(), "user_id": image.user_id, "system_name": image.system_name, "prop_type": image.prop_type, "position": image.position, "binary": img }  
    result = db_dep.post_collection_document(images_collection_name, image_post)
    if call_validate_func_on_data(data=str(result), validate_func=UUID, app_logger=db_dep.app_logger):
        return JSONResponse(content="Successfully added document to collection", status_code=200)
    return JSONResponse(content="Adding document to collection failed. Check image API logs", status_code=405)
