from fastapi import APIRouter

from vpsmon.enums import ProviderType
from vpsmon.models import DataCenter

router = APIRouter()


@router.get("")
async def get_datacenters(provider: ProviderType):
    return await DataCenter.filter(provider=provider)
