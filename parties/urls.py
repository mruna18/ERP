from django.urls import path
from .views import *

urlpatterns = [
    path('types/', PartyTypeListView.as_view(), name='party-types'),
    path('', PartyListPostView.as_view(), name='party-list'),
    path('create/', PartyCreateView.as_view(), name='party-create'),
    path('<int:company_id>/<int:pk>/', PartyDetailView.as_view(), name='party-detail'),
    path('<int:pk>/update/', PartyUpdateView.as_view(), name='party-update'),
    path('<int:pk>/delete/', PartyDeleteView.as_view(), name='party-delete'),
]
