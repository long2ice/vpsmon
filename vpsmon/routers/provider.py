from fastapi import APIRouter
from pydantic import BaseModel

from vpsmon.enums import ProviderType
from vpsmon.models import VPS
from vpsmon.utils import get_providers, get_provider

router = APIRouter()


class Provider(BaseModel):
    name: str
    type: ProviderType
    icon: str


@router.get("", response_model=list[Provider])
async def list_providers():
    providers = get_providers()
    ret = []
    for provider in providers:
        ret.append(provider.dict())
    return ret


@router.get("/{type_}")
async def get_provider_detail(type_: ProviderType):
    provider = get_provider(type_)
    categories = (
        await VPS.filter(provider=provider.type)
        .distinct()
        .order_by("category")
        .values_list("category", flat=True)
    )
    ret = provider.dict()
    ret["categories"] = categories
    return ret
