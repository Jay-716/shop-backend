from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.auth import current_user
from app.models import User, Notification
from app.schemas.order import *

notif_router = APIRouter(prefix="/notif", tags=["通知"])


@notif_router.get("")
async def get_all_notif(user: User = Depends(current_user), db: AsyncSession = Depends(get_async_session)) \
        -> List[Dict[str, Any]]:
    query = select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    notifs = await db.execute(query)
    notifs = notifs.scalars().all()
    return [{"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at} for n in notifs] + [
        {
            "id": 1,
            "title": "欢迎加入商城",
            "content": "欢迎加入本商城。早期开发阶段，测试不完全，如有错误敬请谅解。",
            "created_at": datetime.datetime.now()
        },
    ]

