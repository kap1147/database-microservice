import os
from uuid import UUID
from io import BytesIO
from pathlib import Path
from ..db_conn import DbDependencyServer
from ..pillow.image_setter import pillow_image_setter

bootstrapper_database_name = "BOOTSTRAPPER_DB"
bootstrapper_collection_name = "BOOTSTRAPPER_COL"
db_dep = DbDependencyServer(bootstrapper_database_name, bootstrapper_collection_name, "bootstrapper_logger", "/var/opt/rah_startup.log")()
base_dir = './src/bootstrahpper/assets'

# TODO: maybe just use prop_type

# TODO: update ImageGet to work with sun/moon props

# TODO: check if admin user is created 
# if not, create

# get admin id from user table
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
                prop_type = body.split(".")[0]
                if prop_type in expected_props:
                    image_post = { 
                                    "user_id": admin_id, 
                                    "system_name": system_name, 
                                    "day_or_night": is_day,
                                    "prop_type": prop_type,
                                    "binary": pillow_image_setter(f"{center_mass_dir}/{body}", db_dep.app_logger) 
                                }  
                    db_dep.post_collection_document(bootstrapper_collection_name, image_post)
        
        if os.path.isdir(orbiting_mass_dir):
            for body in os.listdir(orbiting_mass_dir):
                if system_type == "sun" or system_type == "moon":
                    byte_array = BytesIO()
                    try:
                        planet_position = int(body.split("_")[-1].split(".")[0])
                    except ValueError as e:
                        db_dep.app_logger.error(f"Following file is not configured properly: {orbiting_mass_dir}/{body}! Last characters before the extension and after the last underscore should be a number.")
                        continue
                   
                    image_post = { 
                                    "user_id": admin_id, 
                                    "position": planet_position, 
                                    "system_name": system_name, 
                                    "overview_or_details": (planet_position > 9),
                                    "day_or_night": is_day,
                                    "binary": pillow_image_setter(f"{orbiting_mass_dir}/{body}", db_dep.app_logger) 
                                }  
                    db_dep.post_collection_document(bootstrapper_collection_name, image_post)

    db_dep.app_logger.info("Finished bootstrahpping!")
except Exception as e:
    db_dep.app_logger.error(f"Got unexpected error when boostrapping the rah db\n{e} ")