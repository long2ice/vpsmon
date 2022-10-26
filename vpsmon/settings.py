from typing import Optional

import sentry_sdk
from pydantic import BaseSettings
from sentry_sdk.integrations.redis import RedisIntegration


class Settings(BaseSettings):
    DEBUG: bool = False
    DB_URL: str
    REDIS_URL: str
    API_SECRET: str
    ENV = "production"
    SENTRY_DSN: Optional[str]
    TG_BOT_TOKEN: str
    TG_CHAT_ID = "@vpsmonchannel"
    SITE_URL = "https://www.vpsmon.me"

    def vps_link(self, vps_id: int):
        return self.SITE_URL + f"/vps/link?id={vps_id}"

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore

TORTOISE_ORM = {
    "apps": {
        "models": {
            "models": ["vpsmon.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "connections": {"default": settings.DB_URL},
}
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENV,
    integrations=[RedisIntegration()],
    traces_sample_rate=1.0,
)
