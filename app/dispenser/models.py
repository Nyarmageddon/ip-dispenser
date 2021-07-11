from ipaddress import ip_address, ip_network

from django.contrib.auth.models import User
from django.db import models, transaction, IntegrityError


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

    address = models.GenericIPAddressField(unique=True)
    gateway = models.GenericIPAddressField(blank=True, null=True)
    mask = models.IntegerField()
    protocol = models.CharField(max_length=2, choices=PROTOCOLS)

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
        return self.addresses.exclude(owner=None).count()

    @property
    def capacity(self):
        """Максимально возможное число адресов в этой сети."""
        max_bits = 32 if self.protocol == "v4" else 128
        return 2**(max_bits - self.mask) - 1

    @property
    def value(self):
        return ip_network(str(self))

    def get_free_ip(self, new_owner):
        """Выдаёт случайный незанятый IP из этой сети."""
        # Выдаёт IP-адрес, уже добавленный в базу, без текущего владельца
        free_ip = self.addresses.filter(owner=None).order_by("?").first()
        if free_ip:
            try:
                free_ip.claim(new_owner)
            except IPAddress.AlreadyClaimed:
                pass

        if free_ip:
            return free_ip

        # Пытаемся создать новый IP-адрес.
        existing = set(
            ip
            for values in self.addresses.values_list("address")
            for ip in values
        )

        for host in self.value.hosts():
            if host.compressed != self.gateway and host.compressed not in existing:
                break

        free_ip = IPAddress(
            address=host.compressed,
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
