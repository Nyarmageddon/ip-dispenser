from ipaddress import ip_address, ip_network

from django.contrib.auth.models import User
from django.db import models, transaction


class IPSubnet(models.Model):
    """Обозначает подсеть из IP-адресов."""

    address = models.GenericIPAddressField()
    gateway = models.GenericIPAddressField(blank=True, null=True)
    mask = models.IntegerField()

    class Meta:
        verbose_name = "Подсеть IP"
        verbose_name_plural = "Подсети IP"
        ordering = ["address"]

    def __str__(self):
        return f"{self.address}/{self.mask}"

    def __len__(self):
        return self.addresses.count()

    @property
    def value(self):
        return ip_network(self.address)


class IPAddress(models.Model):
    """Обозначает один конкретный IP-адрес."""

    address = models.GenericIPAddressField()
    claimed_at = models.DateTimeField(
        auto_now=True,
        verbose_name="дата выдачи",
    )
    subnet = models.ForeignKey(
        IPSubnet,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="ip_addresses",
    )

    class AlreadyClaimed(Exception):
        pass

    class Meta:
        verbose_name = "IP-адрес"
        verbose_name_plural = "IP-адреса"

    def __str__(self):
        return f"{self.address}"

    @property
    def value(self):
        return ip_address(self.address)

    @property
    def claimed(self):
        return (self.owner is not None)

    def query_set(self):
        """QuerySet, выбирающий этого пользователя."""
        self.__class__.objects.filter(id=self.id)

    @transaction.atomic
    def claim(self, new_owner):
        """Выдать свободный IP-адрес пользователю.
           Передача между пользователями выдаёт ошибку.
        """
        address = self.query_set.select_for_update().get()

        if address.claimed:
            raise IPAddress.AlreadyClaimed("IP-адрес уже занят.")

        self.owner = new_owner
        self.save()

    def abandon(self):
        """Возвращает адрес в пул свободных."""
        self.owner = None
        self.save()
