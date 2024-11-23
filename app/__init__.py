from fastapi import FastAPI

from config import api_root, enable_doc


app_kwargs = {}
if enable_doc:
    app_kwargs |= {"docs_url": None, "redoc_url": None, "openapi_url": None}


app = FastAPI(root_path=api_root, root_path_in_servers=True, **app_kwargs)
