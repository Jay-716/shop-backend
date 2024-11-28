from typing import Dict, Any, List

from fastapi import APIRouter, Depends

from app.auth import current_user
from app.schemas.order import *

notif_router = APIRouter(prefix="/notif", tags=["通知"])


@notif_router.get("", dependencies=[Depends(current_user)])
def get_all_notif() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "title": "欢迎加入商城",
            "content": "欢迎加入本商城。早期开发阶段，测试不完全，如有错误敬请谅解。",
            "created_at": datetime.datetime.now()
        },
    ]

