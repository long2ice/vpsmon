from tortoise import fields
from tortoise.models import Model

from vpsmon.enums import Currency, ProviderType, VPSPeriod


class VPS(Model):
    provider = fields.CharEnumField(ProviderType)
    category = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    memory = fields.IntField(description="RAM in MB")
    cpu = fields.FloatField(description="vCPU")
    disk = fields.FloatField(description="Disk in GB")
    disk_type = fields.CharField(max_length=255, null=True)
    bandwidth = fields.FloatField(description="Bandwidth in GB")
    speed = fields.FloatField(description="Speed in Mbps")
    price = fields.FloatField()
    ipv4 = fields.IntField()
    ipv6 = fields.IntField(default=0)
    link = fields.CharField(max_length=255)
    currency = fields.CharEnumField(Currency, default=Currency.USD)
    period = fields.CharEnumField(VPSPeriod, default=VPSPeriod.month)
    count = fields.IntField(default=-1)

    class Meta:
        unique_together = [("provider", "category", "name")]


class DataCenter(Model):
    provider = fields.CharEnumField(ProviderType)
    name = fields.CharField(max_length=255)
    location = fields.CharField(max_length=255)
    ipv4 = fields.CharField(max_length=255, null=True)
    ipv6 = fields.CharField(max_length=255, null=True)

    class Meta:
        unique_together = [("provider", "name")]
