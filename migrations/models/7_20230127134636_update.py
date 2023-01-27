from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `subscriber` MODIFY COLUMN `chat_id` VARCHAR(255) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `subscriber` MODIFY COLUMN `chat_id` INT NOT NULL;"""
