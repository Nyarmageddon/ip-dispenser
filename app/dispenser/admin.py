from django.contrib import admin

from dispenser.models import IPAddress, IPSubnet


admin.site.site_header = "IP Dispenser"


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    """Интерфейс управления IP-адресами в админке."""

    list_display = ["address", "subnet", "claimed_at", "owner"]
    list_filter = ["subnet", "owner"]
    search_fields = ["address"]


@admin.register(IPSubnet)
class IPSubnetAdmin(admin.ModelAdmin):
    """Интерфейс управления подсетями в админке."""

    list_display = ["__str__", "protocol", "__len__", "capacity"]
