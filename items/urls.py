from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ItemCreateView.as_view()),

    path("", ListItemView.as_view()),
    path("<int:pk>/", RetrieveItemView.as_view()),
    path("<int:pk>/update/", UpdateItemView.as_view()),
    path("<int:pk>/delete/", DeleteItemView.as_view()),
]
