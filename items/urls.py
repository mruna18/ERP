from django.urls import path
from .views import (
    ItemCreateView,
    ListItemView,
    RetrieveItemView,
    UpdateItemView,
    DeleteItemView,
    UnitTypeListView,
)

urlpatterns = [
    path("create/", ItemCreateView.as_view(), name="item-create"),
    path("", ListItemView.as_view(), name="item-list"),
    path("units/", UnitTypeListView.as_view(), name="unit-list"),
    path("<int:company_id>/<int:pk>/", RetrieveItemView.as_view(), name="item-detail"),
    path("<int:company_id>/<int:pk>/update/", UpdateItemView.as_view(), name="update-item"),
    path("<int:company_id>/<int:pk>/delete/", DeleteItemView.as_view(), name="delete-item"),
]
