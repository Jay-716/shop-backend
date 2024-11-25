from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_session
from app.models.banner import Banner
from app.schemas.banner import BannerRead, BannerCreate


banner_router = APIRouter(prefix="/banner", tags=["Banner"])


@banner_router.get("/active")
def get_all_active_banner(db: Session = Depends(get_session)) -> List[BannerRead]:
    query = select(Banner).where(Banner.deleted == False)
    return db.execute(query).scalars().all()
