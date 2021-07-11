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
        "subnet/<int:subnet_id>/delete/",
        staff_member_required(views.delete_subnet),
        name="delete_subnet",
    ),
]
