from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt';
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt';"""
