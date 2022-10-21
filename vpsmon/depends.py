import datetime
import hashlib
import time
from json import JSONDecodeError
from typing import Dict

from fastapi import Header, HTTPException
from pydantic import constr
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from vpsmon.common import RedisKey, redis
from vpsmon.settings import settings


def get_sign(data: Dict, timestamp: int, nonce: str):
    kvs = [f"timestamp={timestamp}", f"nonce={nonce}"]
    for key, value in data.items():
        if value is None:
            continue
        value_str = str(value)
        kvs.append(f"{key}={value_str}")
    to_encode_str = "&".join(sorted(kvs))
    to_encode_str = f"{to_encode_str}&key={settings.API_SECRET}"
    m = hashlib.md5()
    m.update(to_encode_str.encode())
    return m.hexdigest().upper()


async def sign_required(
    request: Request,
    x_sign: str = Header(..., example="sign"),
    x_nonce: constr(curtail_length=8) = Header(..., example="11111111"),  # type:ignore
    x_timestamp: int = Header(..., example=int(time.time())),
):
    if settings.DEBUG:
        return
    if request.url.path in ["/docs", "/openapi.json"]:
        return
    if request.method in ["GET", "DELETE"]:
        data = dict(request.query_params)
    else:
        try:
            data = await request.json()
        except JSONDecodeError:
            data = {}
    now = int(datetime.datetime.now().timestamp())
    if abs(now - x_timestamp) > 60 * 10:
        raise HTTPException(detail="Timestamp expired", status_code=HTTP_403_FORBIDDEN)
    if await redis.sismember(RedisKey.nonce_cache, x_nonce):
        raise HTTPException(detail="Nonce str repeated", status_code=HTTP_403_FORBIDDEN)
    await redis.sadd(RedisKey.nonce_cache, x_nonce)
    verified = get_sign(data, x_timestamp, x_nonce) == x_sign
    if not verified:
        raise HTTPException(detail="Signature verify failed", status_code=HTTP_403_FORBIDDEN)
