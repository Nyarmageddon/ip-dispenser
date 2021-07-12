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
    # 0-й адрес, шлюз и Broadcast-адрес IPv4
    reserved = 3 if net.version == 4 else 2
    return net.num_addresses - reserved
