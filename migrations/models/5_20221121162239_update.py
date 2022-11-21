from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost\ndmit: dmit\nvultr: vultr\nvps: v.ps';
        ALTER TABLE `vps` ADD `remarks` VARCHAR(255);
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost\ndmit: dmit\nvultr: vultr\nvps: v.ps';
        ALTER TABLE `vps` MODIFY COLUMN `period` VARCHAR(9) NOT NULL  COMMENT 'month: month\nyear: year\ntriennium: triennium\nquarterly: quarterly' DEFAULT 'month';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `vps` DROP COLUMN `remarks`;
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost';
        ALTER TABLE `vps` MODIFY COLUMN `period` VARCHAR(9) NOT NULL  COMMENT 'month: month\nyear: year\ntriennium: triennium' DEFAULT 'month';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost';"""
