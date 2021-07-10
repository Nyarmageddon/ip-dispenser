from ipaddress import ip_address, ip_network

from django.contrib.auth.models import User
from django.db import models


class IPSubnet(models.Model):
    """Обозначает подсеть из IP-адресов."""

    address = models.GenericIPAddressField()
    gateway = models.GenericIPAddressField(blank=True, null=True)
    mask = models.IntegerField()

    def __str__(self):
        return f"Подсеть: {self.address}/{self.mask}"

    @property
    def value(self):
        return ip_network(self.address)


class IPAddress(models.Model):
    """Обозначает один конкретный IP-адрес."""

    address = models.GenericIPAddressField()
    subnet = models.ForeignKey(
        IPSubnet,
        on_delete=models.CASCADE, related_name="addresses",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="ip_addresses",
    )

    def __str__(self):
        return f"{self.address} ({self.subnet})"

    def value(self):
        return ip_address(self.address)
