from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_queryset_creator

from vpsmon.enums import ProviderType
from vpsmon.models import VPS

router = APIRouter()


class VPSRes(BaseModel):
    data: pydantic_queryset_creator(VPS, exclude=("link",))
    total: int


@router.get("", response_model=VPSRes)
async def get_vps(
    provider: Optional[ProviderType] = None,
    category: Optional[str] = None,
    cpu: Optional[float] = None,
    memory: Optional[int] = None,
    disk: Optional[float] = None,
    bandwidth: Optional[int] = None,
    speed: Optional[int] = None,
    price: Optional[float] = None,
    period: Optional[str] = None,
    limit: int = Query(8, le=8),
    offset: int = Query(0, ge=0),
):
    qs = VPS.all()
    if provider:
        qs = qs.filter(provider=provider)
    if category:
        qs = qs.filter(category=category)
    if cpu:
        qs = qs.filter(cpu__gte=cpu)
    if memory:
        qs = qs.filter(memory__gte=memory)
    if disk:
        qs = qs.filter(disk__gte=disk)
    if bandwidth:
        qs = qs.filter(bandwidth__gte=bandwidth)
    if speed:
        qs = qs.filter(speed__gte=speed)
    if price:
        qs = qs.filter(price__lte=price)
    if period:
        qs = qs.filter(period=period)
    total = await qs.count()
    qs = qs.order_by("cpu", "memory", "disk").limit(limit).offset(offset)
    return VPSRes(data=await qs, total=total)


class VPSLink(BaseModel):
    link: str


@router.get("/{vps_id}/link", response_model=VPSLink)
async def vps_link(
    vps_id: int,
):
    vps = await VPS.get(id=vps_id)
    return vps
