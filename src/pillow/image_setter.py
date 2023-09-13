from io import BytesIO
from PIL import Image
import logging

def pillow_image_setter(image_filename: str, _app_logger: logging):
    byte_array = BytesIO()
    try:
        img = Image.open(image_filename)
    except Exception as e:
        _app_logger.error(f"Issue loading image. Check image API logs:\n{e}")

    if (image_filename[-3:].lower() == "png"):
        img.save(byte_array, format="PNG")
    elif (image_filename[-3:].lower() == "jpg"):
        img.save(byte_array, format="JPEG")
    else:
        msg = f"Provided unexpected image type. File extension must be either jpg or png. Provided file extension: {image_filename[:-3]}"
        _app_logger.error(msg)
        raise Exception(msg)
    byte_array.seek(0)
    return byte_array