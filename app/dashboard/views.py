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

    model = IPAddress

    template_name = "dashboard/subnet.html"
    context_object_name = "ip_addresses"

    def get_queryset(self):
        return IPAddress.objects.filter(
            subnet=self.kwargs["subnet_id"]
        ).order_by(
            "-claimed_at", "owner"
        ).select_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        network = IPSubnet.objects.get(id=self.kwargs["subnet_id"]).address
        context["network"] = network
        return context


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
