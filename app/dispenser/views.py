from django.shortcuts import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import IPAddress


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
