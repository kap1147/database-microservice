import os
import json
import time
import requests

from uuid import UUID
from io import BytesIO
from pathlib import Path
from ..db_conn import DbDependencyServer
from ..pillow.image_setter import pillow_image_setter

bootstrapper_database_name = "DB_NAME"
bootstrapper_collection_name = "IMAGES_COLLECTION"
db_dep = DbDependencyServer(bootstrapper_database_name, bootstrapper_collection_name, "bootstrapper_logger", "/var/opt/rah_startup.log")()
base_dir = './src/bootstrahpper/assets'

max_retries = 5
wait_seconds = 2
csrf_tok =  ""

if not os.getenv("CSRF_URI"):
    raise ValueError("CSRF_URI environment variable is not set")
for attempt in range(max_retries):
    try:
        csrf_tok =  requests.get(os.getenv("CSRF_URI"))
        csrf_tok.raise_for_status()  
        break  
    except requests.exceptions.RequestException as e:
        if attempt < max_retries - 1:
            time.sleep(wait_seconds)
        else:
          raise e

dun = os.getenv("ADMIN_USER")
did = requests.get(os.getenv("USER_URI"), params={
        # "X-XRSF-TOKEN": csrf_tok,
        "username": dun,
        "Content-Type": "application/json"
    })
db_dep.app_logger.info("Beginning bootstrahpping!")
if not did.text:
  no_did_msg = "Could not find user admin! Ensure auth server is runnning, is reachable, and that it bootstrapped the admin user correctly"
  db_dep.app_logger.info(no_did_msg)
  raise TypeError(no_did_msg)
    
try:
    did = UUID(json.loads(did.text)["id"])
    db_dep.app_logger.info("Preparing to upload assets")
    for system in os.listdir(base_dir):
        system_name = "_".join(system.split("_")[1:])
        system_type = system.split("_")[0]
        is_day = (system_type == "sun")
        system_path = f"{base_dir}/{system}"
        center_mass_dir = f"{system_path}/center_mass_props"
        orbiting_mass_dir = f"{system_path}/orbiting_mass_props"

        db_dep.app_logger.info("Uploading asssets for center mass")
        if os.path.isdir(center_mass_dir):
            expected_props = ["texture", "bumptexture", "lensflare"] 
            for body in os.listdir(center_mass_dir):
                center_mass_prop = body.split(".")[0]
                if center_mass_prop in expected_props:
                    center_prop_position = expected_props.index(center_mass_prop)
                    image_post = { 
                                    "user_id": dun, 
                                    "system_name": system_name, 
                                    "prop_type": f"{system_type}_center_mass",
                                    "position": center_prop_position,
                                    "binary": pillow_image_setter(f"{center_mass_dir}/{body}", db_dep.app_logger) 
                                }  
                    db_dep.post_collection_document(bootstrapper_collection_name, image_post)
        
        db_dep.app_logger.info("Uploading assets for orbitting mass")
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
                                    "user_id": dun, 
                                    "system_name": system_name, 
                                    "prop_type": system_type,
                                    "position": planet_position, 
                                    "binary": pillow_image_setter(f"{orbiting_mass_dir}/{body}", db_dep.app_logger) 
                                }  
                    db_dep.post_collection_document(bootstrapper_collection_name, image_post)
    db_dep.app_logger.info("Finished bootstrahpping!")
except ValueError as e:
    v_err_msg = f"Value error exception thrown when bootstrapping images db. Check if admin user was bootstrapped on auth server statup:\n{e}"
    db_dep.app_logger.error(v_err_msg)
    # raise ValueError(v_err_msg)
except Exception as e:
    g_err_msg = f"Got unexpected error when boostrapping the rah db\n{e}"
    db_dep.app_logger.error(g_err_msg)
    raise Exception (g_err_msg)
