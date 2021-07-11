from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path(
        "",
        staff_member_required(views.AdminDashboardView.as_view()),
        name="main"
    ),
    path(
        "subnet/<int:subnet_id>/",
        staff_member_required(views.AdminSubnetView.as_view()),
        name="subnet",
    ),
    path(
        "user/<int:user_id>/",
        staff_member_required(views.UserIPOverview.as_view()),
        name="user_overview",
    ),
    path(
        "subnet/<int:subnet_id>/delete/",
        views.delete_subnet,
        name="delete_subnet",
    ),
    path(
        "ip/<int:ip_id>/delete/",
        views.delete_ip,
        name="delete_ip"
    ),
]
