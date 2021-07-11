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
