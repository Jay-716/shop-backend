from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

from config import api_root, enable_doc, allow_origins
from .auth import auth_router
from app.routers.user import address_router, user_router
from app.routers.store import store_router
from app.routers.good import good_router, tag_router
from app.routers.order import order_router
from app.routers.pay import pay_router
from app.routers.banner import banner_router
from app.utils.file_utils import file_router


app_kwargs = {}
if not enable_doc:
    app_kwargs |= {"docs_url": None, "redoc_url": None, "openapi_url": None}


app = FastAPI(root_path=api_root, root_path_in_servers=True, **app_kwargs)
add_pagination(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(address_router)
app.include_router(user_router)
app.include_router(store_router)
app.include_router(good_router)
app.include_router(tag_router)
app.include_router(order_router)
app.include_router(pay_router)
app.include_router(banner_router)
app.include_router(file_router)
