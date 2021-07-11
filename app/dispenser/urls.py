from django.contrib.admin.views.decorators import staff_member_required
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
        "dashboard/",
        staff_member_required(views.AdminDashboardView.as_view()),
        name="admin_main"
    ),
    path(
        "subnet/<int:subnet_id>/delete/",
        staff_member_required(views.delete_subnet),
        name="delete_subnet",
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
        "ip/<int:ip_id>/delete/",
        views.delete_ip,
        name="delete_ip",
    ),
]
