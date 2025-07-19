from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CreateCompanyView.as_view(), name='company-create'),
    path('list/', CompanyListView.as_view()),
    path('<int:pk>/', CompanyDetailView.as_view()),
    path('<int:pk>/update/', CompanyUpdateView.as_view()),
    path('<int:pk>/delete/', CompanyDeleteView.as_view()),
    path('select/', SelectCompanyView.as_view(), name='select-company'),
    # path('<int:company_id>/dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
