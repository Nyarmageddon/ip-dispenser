from ipaddress import ip_address, ip_network

from django.contrib.auth.models import User
from django.db import models, transaction


class SubnetManager(models.Manager):
    """Расширенный функционал для управления подсетями."""

    def get_one_with_ips(self):
        """Выдаёт подсеть для получения IP-адреса."""
        # Здесь можно добавить условия для выдачи подсети.
        return self.get_queryset().order_by("?").first()


class IPSubnet(models.Model):
    """Обозначает подсеть из IP-адресов."""

    address = models.GenericIPAddressField(unique=True)
    gateway = models.GenericIPAddressField(blank=True, null=True)
    mask = models.IntegerField()

    objects = SubnetManager()

    class Meta:
        verbose_name = "Подсеть IP"
        verbose_name_plural = "Подсети IP"
        ordering = ["address"]

    class NoFreeAddresses(Exception):
        """В сети закончились IP-адреса."""

    def __str__(self):
        return f"{self.address}/{self.mask}"

    def __len__(self):
        return self.addresses.count()

    @property
    def value(self):
        return ip_network(self.address)

    def get_ip(self, new_owner):
        """Выдаёт случайный незанятый IP из этой сети."""
        # Выдаёт IP-адрес, уже добавленный в базу, без текущего владельца
        free_ip = self.addresses.filter(owner=None).order_by("?").first()
        if free_ip:
            free_ip.claim(new_owner)
        else:
            raise IPSubnet.NoFreeAddresses("Нет свободных IP.")
        return free_ip


class IPAddress(models.Model):
    """Обозначает один конкретный IP-адрес."""

    address = models.GenericIPAddressField(unique=True)
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
        """IP-адрес уже выдан клиенту."""

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
        """QuerySet, выбирающий этот же IP."""
        return self.__class__.objects.filter(id=self.id)

    @transaction.atomic
    def claim(self, new_owner):
        """Выдать свободный IP-адрес пользователю.
           Передача между пользователями выдаёт ошибку.
        """
        address = self.query_set().select_for_update().get()

        if address.claimed:
            raise IPAddress.AlreadyClaimed("IP-адрес уже занят.")

        address.owner = new_owner
        address.save()

    def abandon(self):
        """Возвращает адрес в пул свободных."""
        self.owner = None
        self.save()
