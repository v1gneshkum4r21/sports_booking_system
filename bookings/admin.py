from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Booking
import json
import logging

logger = logging.getLogger(__name__)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'facility', 'date', 'time_slot', 'status', 'created_at']
    list_filter = ['status', 'date', 'facility']
    search_fields = ['user__username', 'facility__name']
    readonly_fields = ['created_at']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('qr-scanner/', self.admin_site.admin_view(self.qr_scanner_view), name='qr-scanner'),
            path('verify-booking/<str:booking_data>/', self.admin_site.admin_view(self.verify_booking), name='verify-booking'),
        ]
        return custom_urls + urls

    def qr_scanner_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'QR Code Scanner',
            # Add any additional context variables here
        }
        return render(request, 'admin/qr_code_scanner.html', context)

    @csrf_protect
    def verify_booking(self, request, booking_data):
        try:
            data = json.loads(booking_data)
            access_token = data.get('access_token')

            booking = Booking.objects.get(access_token=access_token)
            booking.verify()

            return JsonResponse({
                'success': True,
                'booking': {
                    'id': booking.id,
                    'user': booking.user.get_full_name() or booking.user.username,
                    'facility': booking.facility.name,
                    'date': booking.date.strftime('%Y-%m-%d'),
                    'time_slot': str(booking.time_slot),
                    'status': booking.status,
                    'access_token': access_token
                }
            })
        except json.JSONDecodeError as e:
            logger.error(f"Invalid QR code format: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid QR code format'
            }, status=400)
        except Booking.DoesNotExist as e:
            logger.error(f"Booking not found: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error verifying booking: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
