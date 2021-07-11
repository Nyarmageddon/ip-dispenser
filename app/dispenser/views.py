from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import HttpResponse
from django.urls import reverse
from django.views.generic import ListView

from .models import IPAddress, IPSubnet


def dummy(*args):
    """Test."""
    return HttpResponse("It works!")


class UserAccountView(LoginRequiredMixin, ListView):
    """Отображает интерфейс пользователя для работы с IP."""

    login_url = "dispenser:login"

    template_name = "dispenser/account.html"
    context_object_name = "ip_addresses"

    def get_queryset(self):
        addresses = IPAddress.objects.filter(owner_id=self.request.user)
        return addresses.order_by("-claimed_at")


class AdminDashboardView(ListView):
    """Главная страница администратора для работы с подсетями и IP."""

    model = IPSubnet

    template_name = "dispenser/admin.html"
    context_object_name = "ip_networks"


def delete_subnet(request: HttpRequest, subnet_id: int):
    """Удаление подсети администратором."""
    try:
        subnet = IPSubnet.objects.get(id=subnet_id)
    except ObjectDoesNotExist:
        raise Http404()

    if not request.user.is_staff:
        return HttpResponseForbidden

    subnet.delete()
    return HttpResponseRedirect(reverse("dispenser:admin_main"))


def delete_ip(request: HttpRequest, ip_id: int):
    """Удаляет IP-адрес, принадлежащий пользователю, из базы."""
    try:
        address = IPAddress.objects.get(id=ip_id)
    except ObjectDoesNotExist:
        raise Http404()

    if address.owner != request.user:
        raise Http404()

    address.abandon()
    return HttpResponseRedirect(reverse("dispenser:account"))
