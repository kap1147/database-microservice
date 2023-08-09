import os
import json
import gridfs
import logging
import contextlib

from io import BytesIO
from typing import Dict
from uuid import UUID, uuid4
from fastapi import HTTPException

from .logger import setup_logger

from dotenv import load_dotenv
from pymongo import MongoClient

#todo: null check? do i even care?
#also, better exception handling but again ????? dirgaf

class DbConnection:
    def __init__(self, _app_logger: logging) -> None:
        self.app_logger = _app_logger

    @contextlib.contextmanager
    def get_db_conn(self):
        load_dotenv()
        dbuser = os.getenv("DB_USER")
        dbpass = os.getenv("DB_PASS")
        imagesdb = os.getenv("IMAGES_DB")
  
        urlconn = f"mongodb://{dbuser}:{dbpass}@localhost:27017/"

        if (urlconn.count("@") > 1 or urlconn.count(":") > 3):
            raise ValueError(f"Do not include string '@' or ':' in DB_USER: {dbuser} or DB_PASS: {dbpass}")

        conn = MongoClient(urlconn,  UuidRepresentation='standard')
        curr_dbs = conn.list_database_names()
        if (imagesdb not in curr_dbs):
            raise ValueError(f"Expected to have existing MongoDB database '{imagesdb}' but not found!")

        try:
            yield conn[imagesdb]
        except Exception as e:
            self.app_logger.exception(e)
            print(e)
        finally:                
            conn.close()

    def get_collection_from_env(self, col_name: str):
        if any(char in col_name for char in [".", "$",]) or col_name.startswith("system"):
           raise ValueError(f"Invalid images collection name: {col_name}")
        return os.getenv(col_name)

    def get_collection_names(self):
        try:
            with self.get_db_conn() as conn:
                return conn.list_collection_names()
        except Exception as e:
            self.app_logger.exception(e)
            print(e)

    def get_collection_document(self, collection_name: str, query: Dict):
        with self.get_db_conn() as conn:
            try:
                colconn = gridfs.GridFS(conn, collection=self.get_collection_from_env(collection_name))
                return colconn.find_one(query)
            except Exception as e:
                self.app_logger.exception(e)
                print(e)

    def post_collection_document(self, collection_name: str, query: Dict):
        with self.get_db_conn() as conn:
            try:
                colconn = gridfs.GridFS(conn, collection=self.get_collection_from_env(collection_name))
                query["binary"] = query["binary"].getvalue()
                return colconn.put(query['binary'], **query)
            except Exception as e:
                self.app_logger.exception(e)
                print(e)


class DbDependencyServer:
    def __init__(self, name: str, path_to_log: str):
        self.name = name
        self.path_to_log = path_to_log

    def __call__(self):
        if self.name and self.path_to_log:
            return DbConnection(setup_logger(self.name, self.path_to_log))
        raise ValueError("Unable to inject app's database dependency!")

