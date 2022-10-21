from typing import Optional

from fastapi import APIRouter, Query

from vpsmon.enums import ProviderType
from vpsmon.models import VPS

router = APIRouter()


@router.get("")
async def get_vps(
    provider: Optional[ProviderType] = None,
    category: Optional[str] = None,
    limit: int = Query(20, le=20),
    offset: int = Query(0, ge=0),
):
    qs = VPS.all()
    if provider:
        qs = qs.filter(provider=provider)
    if category:
        qs = qs.filter(category=category)
    qs = qs.limit(limit).offset(offset)
    return await qs
