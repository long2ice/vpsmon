from fastapi import APIRouter, Depends

from vpsmon.routers import datacenter, provider, vps

router = APIRouter()
router.include_router(provider.router, prefix="/provider", tags=["Provider"])
router.include_router(datacenter.router, prefix="/datacenter", tags=["DataCenter"])
router.include_router(vps.router, prefix="/vps", tags=["VPS"])
