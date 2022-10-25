from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone';
        ALTER TABLE `vps` MODIFY COLUMN `period` VARCHAR(9) NOT NULL  COMMENT 'month: month\nyear: year\ntriennium: triennium' DEFAULT 'month';
        ALTER TABLE `vps` MODIFY COLUMN `period` VARCHAR(9) NOT NULL  COMMENT 'month: month\nyear: year\ntriennium: triennium' DEFAULT 'month';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack';
        ALTER TABLE `vps` MODIFY COLUMN `period` VARCHAR(5) NOT NULL  COMMENT 'month: month\nyear: year' DEFAULT 'month';
        ALTER TABLE `vps` MODIFY COLUMN `period` VARCHAR(5) NOT NULL  COMMENT 'month: month\nyear: year' DEFAULT 'month';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack';"""
