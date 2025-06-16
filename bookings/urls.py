from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('create/<int:facility_id>/', views.booking_create, name='booking_create'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('<int:pk>/edit_bookings',views.booking_edit,name='booking_edit'),
    
    
    path('qr-scanner/', views.qr_scanner, name='qr_scanner'),
    path('verify-booking/<str:booking_data>/', views.verify_booking, name='verify_booking'),
    # If you need a verify-qr endpoint, define it here
    path('verify-qr/', views.verify_qr, name='verify_qr'),
]
