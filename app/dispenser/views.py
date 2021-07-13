from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView

from .models import IPAddress, IPSubnet


class UserAccountView(LoginRequiredMixin, ListView):
    """Отображает интерфейс пользователя для работы с IP."""

    login_url = "dispenser:login"

    template_name = "dispenser/account.html"
    context_object_name = "ip_addresses"

    paginate_by = 10

    def get_queryset(self):
        addresses = IPAddress.objects.filter(owner_id=self.request.user)
        return addresses.order_by("-claimed_at")


@login_required(login_url="dispenser:login")
def get_ip(request, protocol):
    """Выдаёт свободный IP-адрес пользователю."""
    try:
        subnet = IPSubnet.objects.get_network_with_ips(protocol)
        new_ip = subnet.get_free_ip(request.user)
    except IPSubnet.NoFreeAddresses:
        new_ip = None

    if new_ip:
        messages.info(request, f"Выдан IP-адрес {new_ip}")
    else:
        messages.error(
            request,
            "Не удалось получить IP-адрес. Попробуйте повторить попытку позже")
    return HttpResponseRedirect(reverse("dispenser:account"))


@login_required(login_url="dispenser:login")
def delete_ip(request: HttpRequest, ip_id: int):
    """Удаляет IP-адрес, принадлежащий пользователю, из базы."""
    try:
        address = IPAddress.objects.get(id=ip_id)
    except ObjectDoesNotExist:
        raise Http404()

    if address.owner != request.user:
        raise Http404()

    address.abandon()
    messages.info(request, f"{address} удалён")
    return HttpResponseRedirect(reverse("dispenser:account"))
