from itertools import chain as flatten

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction, IntegrityError

import dispenser.ip_util as ip_util


class SubnetManager(models.Manager):
    """Расширенный функционал для управления подсетями."""

    def get_network_with_ips(self, protocol):
        """Выдаёт подсеть для получения IP-адреса."""
        # Здесь можно добавить условия для выдачи подсети.
        networks = self.get_queryset().filter(protocol=protocol).order_by("?")
        for network in networks:
            if len(network) < network.capacity:
                return network
        raise IPSubnet.NoFreeAddresses("Закончились свободные подсети.")


class IPSubnet(models.Model):
    """Обозначает подсеть из IP-адресов."""

    PROTOCOLS = (
        ("v4", "IPv4"),
        ("v6", "IPv6"),
    )

    address = models.GenericIPAddressField(
        unique=True,
        verbose_name="адрес подсети",
    )

    gateway = models.GenericIPAddressField(
        verbose_name="адрес шлюза",
    )

    mask = models.IntegerField(
        verbose_name="маска подсети",
        validators=[MinValueValidator(0), MaxValueValidator(128)],
    )

    protocol = models.CharField(
        max_length=2,
        choices=PROTOCOLS,
        verbose_name="протокол",
    )

    objects = SubnetManager()

    class Meta:
        verbose_name = "Подсеть IP"
        verbose_name_plural = "Подсети IP"
        ordering = ["address"]

    class NoFreeAddresses(Exception):
        """В сети закончились IP-адреса."""

    def __str__(self):
        return f"{self.address}/{self.mask}"

    @admin.display(description="выдано адресов")
    def __len__(self):
        return self.claimed_addresses().count()

    def claimed_addresses(self):
        """Занятые IP-адреса в этой подсети."""
        return self.addresses.exclude(owner=None)

    def unclaimed_addresses(self):
        """Незанятые IP-адреса в этой подсети."""
        return self.addresses.filter(owner=None)

    @property
    @admin.display(description="всего адресов", ordering="mask")
    def capacity(self):
        """Максимально возможное число адресов в этой сети."""
        return ip_util.network_capacity(str(self))

    def clean(self):
        # Проверка соответствия сети и маски.
        if not ip_util.network_valid(str(self)):
            raise ValidationError("Введена некорректная подсеть.")

        # Проверка версии протокола.
        if ip_util.network_protocol(str(self)) != self.protocol:
            raise ValidationError("Указана неправильная версия IP.")

        # Запрет на маленькие подсети.
        if self.capacity <= 0:
            raise ValidationError("Из этой подсети не получится выдать IP.")

        # Проверка принадлежности шлюза к сети.
        if not ip_util.address_in_net(self.gateway, str(self)):
            raise ValidationError("Шлюз не принадлежит этой подсети.")

        # Проверка, что подсеть не является подсетью другой сети.
        other_nets = IPSubnet.objects.filter(
            protocol=self.protocol
        ).exclude(id=self.id)

        if any(ip_util.subnet_of(str(self), str(other))
               for other in other_nets
               ):
            raise ValidationError("Подсеть принадлежит другой сети.")

        # Ни одна из сетей не входит во вновь добавленную.
        if any(ip_util.subnet_of(str(other), str(self))
               for other in other_nets
               ):
            raise ValidationError("Для этой сети уже есть подсети.")

        return super().clean()

    def get_free_ip(self, new_owner):
        """Выдаёт случайный незанятый IP из этой сети."""
        # Выдаёт IP-адрес, уже добавленный в базу, без текущего владельца
        free_ip = self.unclaimed_addresses().order_by("?").first()
        if free_ip:
            try:
                free_ip.claim(new_owner)
            except IPAddress.AlreadyClaimed:
                pass

        if free_ip:
            return free_ip

        # Пытаемся создать новый IP-адрес.
        existing = flatten.from_iterable(self.addresses.values_list("address"))

        hostname = ip_util.get_available_host(
            str(self),
            gateway=self.gateway,
            existing=existing
        )
        free_ip = IPAddress(
            address=hostname,
            owner=new_owner,
            subnet=self,
        )

        try:
            free_ip.save()
        except IntegrityError:
            raise IPSubnet.NoFreeAddresses("Нет свободных IP.")
        return free_ip


class IPAddress(models.Model):
    """Обозначает один конкретный IP-адрес."""

    address = models.GenericIPAddressField(unique=True, verbose_name="адрес")

    claimed_at = models.DateTimeField(
        auto_now=True,
        verbose_name="дата выдачи",
    )

    subnet = models.ForeignKey(
        IPSubnet,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="подсеть",
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="ip_addresses",
        verbose_name="владелец",
    )

    class AlreadyClaimed(Exception):
        """IP-адрес уже выдан клиенту."""

    class Meta:
        verbose_name = "IP-адрес"
        verbose_name_plural = "IP-адреса"

    def __str__(self):
        return f"{self.address}"

    @property
    def claimed(self):
        return (self.owner is not None)

    def query_set(self):
        """QuerySet, выбирающий этот же IP."""
        return self.__class__.objects.filter(id=self.id)

    @transaction.atomic
    def claim(self, owner):
        """Выдать свободный IP-адрес пользователю.
           Передача между пользователями выдаёт ошибку.
        """
        address = self.query_set().select_for_update().get()

        if address.claimed:
            raise IPAddress.AlreadyClaimed("IP-адрес уже занят.")

        address.owner = owner
        address.save()

    def abandon(self):
        """Возвращает адрес в пул свободных."""
        self.owner = None
        self.save()
