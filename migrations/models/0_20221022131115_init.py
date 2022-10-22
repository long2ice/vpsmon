from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `datacenter` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `provider` VARCHAR(10) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicoud: licoud',
    `name` VARCHAR(255) NOT NULL,
    `location` VARCHAR(255) NOT NULL,
    `ipv4` VARCHAR(255),
    `ipv6` VARCHAR(255),
    UNIQUE KEY `uid_datacenter_provide_69e160` (`provider`, `name`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `vps` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `provider` VARCHAR(10) NOT NULL  COMMENT 'racknerd: racknerd\ngreencloud: greencloud\nlicoud: licoud',
    `category` VARCHAR(255) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `ram` INT NOT NULL  COMMENT 'RAM in MB',
    `cpu` DOUBLE NOT NULL  COMMENT 'vCPU',
    `disk` DOUBLE NOT NULL  COMMENT 'Disk in GB',
    `disk_type` VARCHAR(255),
    `bandwidth` DOUBLE NOT NULL  COMMENT 'Bandwidth in GB',
    `speed` DOUBLE NOT NULL  COMMENT 'Speed in Mbps',
    `price` DOUBLE NOT NULL,
    `ipv4` INT NOT NULL,
    `ipv6` INT NOT NULL  DEFAULT 0,
    `link` VARCHAR(255) NOT NULL,
    `currency` VARCHAR(3) NOT NULL  COMMENT 'USD: USD\nEUR: EUR\nGBP: GBP\nCAD: CAD\nAUD: AUD\nJPY: JPY\nCNY: CNY' DEFAULT 'USD',
    `period` VARCHAR(5) NOT NULL  COMMENT 'month: month\nyear: year' DEFAULT 'month',
    `count` INT NOT NULL  DEFAULT -1,
    UNIQUE KEY `uid_vps_provide_d891ee` (`provider`, `category`, `name`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
