from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ItemCreateView.as_view()),

    path("", ListItemView.as_view()),
    path("<int:company_id>/<int:pk>/", RetrieveItemView.as_view()),
path("<int:company_id>/<int:pk>/update/", UpdateItemView.as_view(), name="update-item"),
path("<int:company_id>/<int:pk>/delete/", DeleteItemView.as_view(), name="delete-item"),

]
