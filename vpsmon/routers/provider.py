from fastapi import APIRouter

from vpsmon.utils import get_providers

router = APIRouter()


@router.get("")
async def list_providers():
    providers = get_providers()
    ret = []
    for provider in providers:
        ret.append(provider.dict())
    return ret
