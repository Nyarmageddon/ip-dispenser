from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView

from dispenser.models import IPAddress, IPSubnet


class AdminDashboardView(ListView):
    """Главная страница администратора для работы с подсетями и IP."""

    model = IPSubnet

    template_name = "dashboard/main.html"
    context_object_name = "ip_networks"


class AdminSubnetView(ListView):
    """Страница администратора для просмотра выданных IP."""

    template_name = "dashboard/subnet.html"
    context_object_name = "ip_addresses"

    def get_queryset(self):
        return IPSubnet.objects.all().get(
            id=self.kwargs["subnet_id"]
        ).addresses.order_by(
            "-claimed_at", "owner"
        ).exclude(
            owner=None
        ).select_related("owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        network = IPSubnet.objects.get(id=self.kwargs["subnet_id"]).address
        context["network"] = network
        return context


class UserIPOverview(ListView):
    """Страница для просмотра IP-адресов пользователя."""

    template_name = "dashboard/subnet.html"
    context_object_name = "ip_addresses"

    def get_queryset(self):
        return IPAddress.objects.filter(
            owner_id=self.kwargs["user_id"]
        ).order_by(
            "-subnet", "-claimed_at",
        ).select_related("subnet")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = User.objects.get(id=self.kwargs["user_id"]).username
        context["username"] = username
        return context


@staff_member_required
def delete_ip(request, ip_id):
    """Удаление IP-адреса администратором."""
    try:
        address = IPAddress.objects.select_related("subnet").get(id=ip_id)
    except ObjectDoesNotExist:
        raise Http404()

    if not request.user.is_staff:
        return HttpResponseForbidden

    address.abandon()

    page_back = reverse(
        "dashboard:subnet",
        args=[address.subnet_id],
    )
    return HttpResponseRedirect(page_back)


@staff_member_required
def delete_subnet(request: HttpRequest, subnet_id: int):
    """Удаление подсети администратором."""
    try:
        subnet = IPSubnet.objects.get(id=subnet_id)
    except ObjectDoesNotExist:
        raise Http404()

    if not request.user.is_staff:
        return HttpResponseForbidden

    subnet.delete()
    return HttpResponseRedirect(reverse("dashboard:main"))
