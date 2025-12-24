from django.urls import path, include
from . import views


app_name = "apis"

urlpatterns = [
    path(
        "review/",
        views.create_or_update_review,
        name="create_or_update_review",
    ),
]
