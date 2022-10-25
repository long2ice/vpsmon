from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt';
        ALTER TABLE `vps` ADD `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `vps` ADD `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `vps` DROP COLUMN `created_at`;
        ALTER TABLE `vps` DROP COLUMN `updated_at`;
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(11) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone';"""
