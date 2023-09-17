import os
from uuid import UUID
from io import BytesIO
from pathlib import Path
from ..db_conn import DbDependencyServer
from ..pillow.image_setter import pillow_image_setter

bootstrapper_database_name = "IMAGES_DB"
bootstrapper_collection_name = "IMAGES_COLLECTION"
db_dep = DbDependencyServer(bootstrapper_database_name, bootstrapper_collection_name, "bootstrapper_logger", "/var/opt/rah_startup.log")()
base_dir = './src/bootstrahpper/assets'

# TODO: check if admin user is created. get id 
# if not, create

admin_id = UUID("73db01fe-741c-4219-85e6-be98c77e1b20")
db_dep.app_logger.info("Beginning bootstrahpping!")

try:
    for system in os.listdir(base_dir):
        system_name = "_".join(system.split("_")[1:])
        system_type = system.split("_")[0]
        is_day = (system_type == "sun")
        system_path = f"{base_dir}/{system}"
        center_mass_dir = f"{system_path}/center_mass_props"
        orbiting_mass_dir = f"{system_path}/orbiting_mass_props"

        if os.path.isdir(center_mass_dir):
            expected_props = ["texture", "bumptexture", "lensflare"] 
            for body in os.listdir(center_mass_dir):
                center_mass_prop = body.split(".")[0]
                if center_mass_prop in expected_props:
                    center_prop_position = expected_props.index(center_mass_prop)
                    image_post = { 
                                    "user_id": admin_id, 
                                    "system_name": system_name, 
                                    "prop_type": f"{system_type}_center_mass",
                                    "position": center_prop_position,
                                    "binary": pillow_image_setter(f"{center_mass_dir}/{body}", db_dep.app_logger) 
                                }  
                    db_dep.post_collection_document(bootstrapper_collection_name, image_post)
        
        if os.path.isdir(orbiting_mass_dir):
            for body in os.listdir(orbiting_mass_dir):
                if system_type == "sun" or system_type == "moon":
                    byte_array = BytesIO()
                    try:
                        planet_position = int(body.split("_")[-1].split(".")[0])
                        if planet_position > 11:
                            continue
                    except ValueError as e:
                        db_dep.app_logger.error(f"Following file is not configured properly: {orbiting_mass_dir}/{body}! Last characters before the extension and after the last underscore should be a number.")
                        continue
                   
                    image_post = { 
                                    "user_id": admin_id, 
                                    "system_name": system_name, 
                                    "prop_type": system_type,
                                    "position": planet_position, 
                                    "binary": pillow_image_setter(f"{orbiting_mass_dir}/{body}", db_dep.app_logger) 
                                }  
                    db_dep.post_collection_document(bootstrapper_collection_name, image_post)

    db_dep.app_logger.info("Finished bootstrahpping!")
except Exception as e:
    db_dep.app_logger.error(f"Got unexpected error when boostrapping the rah db\n{e} ")