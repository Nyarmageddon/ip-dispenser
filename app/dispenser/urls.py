from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from . import views

app_name = "dispenser"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="dispenser/main.html"),
        name="main",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="dispenser/login.html",),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "account/",
        views.UserAccountView.as_view(),
        name="account",
    ),
    path(
        "get_ip/",
        views.get_ip,
        name="get_ip",
    ),
    path(
        "ip/<int:ip_id>/delete/",
        views.delete_ip,
        name="delete_ip",
    ),
]
