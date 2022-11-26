from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL;
        CREATE TABLE IF NOT EXISTS `subscriber` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `chat_id` INT NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `vps_id` INT NOT NULL,
    UNIQUE KEY `uid_subscriber_vps_id_150a11` (`vps_id`, `chat_id`),
    CONSTRAINT `fk_subscrib_vps_56c24aec` FOREIGN KEY (`vps_id`) REFERENCES `vps` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `vps` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost\ndmit: dmit\nvultr: vultr\nvps: v.ps';
        ALTER TABLE `datacenter` MODIFY COLUMN `provider` VARCHAR(13) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicloud: licloud\npacificrack: pacificrack\ncloudcone: cloudcone\ndigitalvirt: digitalvirt\nbandwagonhost: bandwagonhost\ndmit: dmit\nvultr: vultr\nvps: v.ps';
        DROP TABLE IF EXISTS `subscriber`;"""
