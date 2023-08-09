from uuid import UUID, uuid4
from typing import BinaryIO, Annotated
from io import BytesIO
from PIL import Image as pilImage

from fastapi import APIRouter, Depends, Query, FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from ..db_conn import DbDependencyServer
from ..models.images import Image
from ..validator.validate import call_validate_func_on_data

image_router = APIRouter()
images_collection_name = "IMAGES_COLLECTION"
db_dep = DbDependencyServer("images_logger", "/var/opt/user_images/images_logger.log")
DatabaseDep = Annotated[DbDependencyServer, Depends(db_dep)]

@image_router.get("/image/")
def get_image(
            db_dep : DatabaseDep,
            user_id: str = Query(None, title="User id"), 
            day_or_night: bool = Query(None, title="Day or night"), 
            overview_or_details: bool = Query(None, title="Overview or details"), 
            position : int = Query(None, title="Which image"),
        ):
    image_query = {'user_id': UUID(user_id), 'position': position, 'day_or_night': day_or_night, 'overview_or_details': overview_or_details}
    get_img = db_dep.get_collection_document(images_collection_name, image_query)

    if get_img:
        # return { "user_id": str(getattr(get_img, "user_id")), 
        #         "position": int(getattr(get_img, "position")), 
        #         "day_or_night": bool(getattr(get_img, "day_or_night")), 
        #         "overview_or_details":bool(getattr(get_img, "overview_or_details")), 
        #         "binary": getattr(get_img, "binary")
        #     }
        return StreamingResponse(BytesIO(getattr(get_img, "binary")), media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Item not found")

@image_router.post("/image/")
def post_image(
            db_dep : DatabaseDep,
            image: Image
        ) -> JSONResponse:
    byte_array = BytesIO()
    
    try:
        img = pilImage.open(image.filename)
    except Exception as e:
        msg = f"Issue loading image. Check image API logs:\n{e}"
        db_dep.app_logger.error(msg)
        return JSONResponse(content=msg, status_code=400)

    if (image.filename[-3:].lower() == "png"):
        img.save(byte_array, format="PNG")
    elif (image.filename[-3:].lower() == "jpg"):
        img.save(byte_array, format="JPEG")
    else:
        msg = f"Provided unexpected image type. File extension must be either jpg or png. Provided file extension: {image.filename[:-3]}"
        db_dep.app_logger.error(msg)
        return JSONResponse(content=msg, status_code=400)

    byte_array.seek(0)
    image_post = { "_id": uuid4(), "user_id": image.user_id, "position": image.position, "overview_or_details": image.overview_or_details,"day_or_night": image.day_or_night, "binary": byte_array }  
    result = db_dep.post_collection_document(images_collection_name, image_post)
    if call_validate_func_on_data(data=str(result), validate_func=UUID, app_logger=db_dep.app_logger):
        return JSONResponse(content="Successfully added document to collection", status_code=200)
    return JSONResponse(content="Adding document to collection failed. Check image API logs", status_code=405)
