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

from pymongo import MongoClient

#todo: null check? do i even care?
#also, better exception handling but again ????? dirgaf

class DbConnection:
    def __init__(self, dbname: str, collection: str, _app_logger: logging) -> None:
        self.app_logger = _app_logger
        self.dbname = dbname
        self.collection = collection

    @contextlib.contextmanager
    def get_db_conn(self):
        dbuser = os.getenv("DB_USER")
        dbpass = os.getenv("DB_PASS")
        givendb = os.getenv(self.dbname)
  
        urlconn = f"mongodb://{dbuser}:{dbpass}@localhost:27017/"

        if (urlconn.count("@") > 1 or urlconn.count(":") > 3):
            raise ValueError(f"Do not include string '@' or ':' in DB_USER: {dbuser} or DB_PASS: {dbpass}")

        conn = MongoClient(urlconn,  UuidRepresentation='standard')
        curr_dbs = conn.list_database_names()
        if (givendb not in curr_dbs):
            raise ValueError(f"Expected to have existing MongoDB database '{givendb}' but not found!")

        try:
            yield conn[givendb]
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
                img_get_query = {k: v for k, v in query.items() if k != "binary"}
                colconn = gridfs.GridFS(conn, collection=self.get_collection_from_env(collection_name))
                query["binary"] = query["binary"].getvalue()
                if (hasattr(self.get_collection_document(collection_name,img_get_query), "_file")):
                    return self.app_logger.info(f"Cannot add image to db. Image already exists for query: {img_get_query}")
                return colconn.put(query['binary'], **query)
            except Exception as e:
                self.app_logger.exception(e)
                print((e))

class DbDependencyServer:
    def __init__(self, db_name:str, db_col: str, logger_name: str, path_to_log: str):
        self.db_name = db_name
        self.db_col = db_col
        self.logger_name = logger_name
        self.path_to_log = path_to_log

    def __call__(self):
        if self.logger_name and self.path_to_log:
            return DbConnection(self.db_name, self.db_col, setup_logger(self.logger_name, self.path_to_log))
        raise ValueError("Unable to inject app's database dependency!")

