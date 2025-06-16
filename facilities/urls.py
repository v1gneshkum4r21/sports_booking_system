from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('', views.facility_list, name='list'),
    path('search/', views.facility_search, name='facility_search'),
    path('<int:id>/', views.facility_detail, name='detail'),
    path('check-availability/', views.check_availability, name='check-availability'),
] 