from fastapi import FastAPI
from fastapi_pagination import add_pagination

from config import api_root, enable_doc
from auth import auth_router
from app.routers.user import address_router
from app.routers.store import store_router


app_kwargs = {}
if not enable_doc:
    app_kwargs |= {"docs_url": None, "redoc_url": None, "openapi_url": None}


app = FastAPI(root_path=api_root, root_path_in_servers=True, **app_kwargs)
add_pagination(app)

app.include_router(auth_router)
app.include_router(address_router)
app.include_router(store_router)
