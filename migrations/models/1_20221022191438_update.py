from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(10) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicoud: licoud';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(10) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicoud: licoud';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(10) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicoud: licoud';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(10) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicoud: licoud';"""
