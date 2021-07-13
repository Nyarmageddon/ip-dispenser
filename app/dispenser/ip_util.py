"""Вспомогательный модуль для математики с IP-адресами."""

from ipaddress import ip_network
from typing import Iterable


def all_hosts(network: str, gateway: str = None) -> Iterable[str]:
    """Все возможные адреса в подсети, за исключением шлюза."""
    return (
        ip.compressed
        for ip in ip_network(network).hosts()
        if ip != gateway
    )


def get_available_host(network: str, *,
                       gateway: str = None, existing: Iterable[str]) -> str:
    """Получить IP-адрес из сети, не выданный раньше."""
    taken_ips = set(existing)
    if gateway:
        taken_ips.add(gateway)
    for host in all_hosts(network, gateway):
        if host not in taken_ips:
            return host


def network_capacity(network: str) -> int:
    """Количество доступных адресов в подсети IPv4 или IPv6."""
    net = ip_network(network)
    # Нулевой адрес, шлюз; Broadcast-адрес для IPv4
    reserved = 3 if net.version == 4 else 2
    return net.num_addresses - reserved


def network_valid(network: str) -> bool:
    """Является ли сеть валидной?"""
    try:
        ip_network(network)
    except ValueError:
        return False
    return True


def network_private(network: str) -> bool:
    """Является ли сеть приватной."""
    return ip_network(network).is_private


def subnet_of(network: str, other: str) -> bool:
    """Является ли первая сеть подсетью второй?"""
    return ip_network(network).subnet_of(ip_network(other))


def address_in_net(address: str, network: str) -> bool:
    """Находится ли IP-адрес в этой сети"""
    return address in all_hosts(network)


def network_protocol(network: str) -> str:
    """Версия протокола: IPv4 или IPv6"""
    return f"v{ip_network(network).version}"
