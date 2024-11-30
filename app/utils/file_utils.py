import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional, Annotated

from fastapi import APIRouter, UploadFile, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, UUID4, AfterValidator

from app.auth import current_user, current_superuser
from config import FILE_BLOCK_SIZE, STORAGE_PATH
from .log_utils import logger

STORAGE_PATH = Path(STORAGE_PATH)
STORAGE_PATH.mkdir(exist_ok=True)

file_router = APIRouter(prefix="/file", tags=["文件"])


class UploadResult(BaseModel):
    ok: bool
    err: Optional[int] = None
    msg: Optional[str] = None
    key: Optional[str] = None


@file_router.get("/validate-exist")
def validate_key_exist(key: str) -> bool:
    storage_dst = STORAGE_PATH / key
    return storage_dst.exists() and storage_dst.is_file()


@file_router.get("/validate")
def validate_key(key: str) -> bool:
    if not key or key.startswith("/"):
        return False
    else:
        return True


# TODO: validate file ids in schemas
def key_validator(v: str) -> str:
    assert validate_key(v), f"key=`{v}` invalid"
    return v


def key_exist_validator(v: str) -> str:
    assert validate_key(v), f"key=`{v}` invalid"
    assert validate_key_exist(v), f"key=`{v}` not exists"
    return v


@file_router.post("/upload")
async def upload_file(file: UploadFile, key: Annotated[str, Query(), AfterValidator(key_validator)]) -> UploadResult:
    try:
        storage_dst = STORAGE_PATH / key
        storage_dst.parent.mkdir(parents=True, exist_ok=True)
        if storage_dst.exists():
            logger.warn(f"upload_file: duplicate key: {key}")
            return UploadResult(ok=False, err=2, msg="duplicate", key=None)
        with open(storage_dst, "wb+") as f:
            while contents := await file.read(FILE_BLOCK_SIZE):
                f.write(contents)
    except Exception as e:
        logger.error(f"upload_file: unknown error", exc_info=e)
        return UploadResult(ok=False, err=-1, msg="unknown", key=None)
    return UploadResult(ok=True, key=key)


@file_router.get("/download")
def download_file(key: Annotated[str, Query(), AfterValidator(key_exist_validator)]) -> FileResponse:
    try:
        file_path = STORAGE_PATH / str(key)
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
    except Exception as e:
        logger.error(f"download: unknown error", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="未知错误")


def save_file_by_byte(data: bytes, key: str):
    dst = STORAGE_PATH / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "wb+") as f:
        f.write(data)


def save_file_buffer(data: BytesIO, key: str):
    dst = STORAGE_PATH / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "wb+") as f:
        while buf := data.read(FILE_BLOCK_SIZE):
            f.write(buf)


def gen_id() -> UUID4:
    return uuid.uuid4()
