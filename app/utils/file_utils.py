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


@file_router.post("/validate")
def validate_key(key: str) -> bool:
    if not key or key.startswith("/"):
        return False
    storage_dst = STORAGE_PATH / key
    return storage_dst.exists() and storage_dst.is_file()


def key_validator(v: str) -> str:
    assert validate_key(v), f"file key=`{v}` not exists"
    return v


@file_router.post("/upload", dependencies=[Depends(current_superuser)])
async def upload_file(file: UploadFile, key: str) -> UploadResult:
    try:
        if not key:
            key = str(gen_id())
        if key.startswith("/"):
            logger.warn(f"upload_file: invalid key: {key}")
            return UploadResult(ok=False, err=1, msg="invalid key", key=None)
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


@file_router.get("/download", dependencies=[Depends(current_user)])
def download_file(file_id: Annotated[str, Query(), AfterValidator(key_validator)]) -> FileResponse:
    try:
        file_path = STORAGE_PATH / str(file_id)
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
