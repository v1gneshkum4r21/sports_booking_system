from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils import timezone
from .models import Booking
from .forms import BookingForm
from facilities.models import Facility
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def booking_create(request, facility_id):
    facility = get_object_or_404(Facility, pk=facility_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.facility = facility

            if Booking.objects.filter(
                facility=facility,
                date=booking.date,
                time_slot=booking.time_slot
            ).exists():
                messages.error(
                    request, 'This time slot is already booked. Please choose another one.')
            else:
                booking.save()
                messages.success(request, 'Booking created successfully!')
                return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {'form': form, 'facility': facility})


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        form = BookingForm(instance=booking)
    return render(request, 'bookings/booking_form.html', {'form': form, 'booking': booking})


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('bookings:booking_list')
    return render(request, 'bookings/booking_confirm_delete.html', {'booking': booking})


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/booking_confirmation.html', {'booking': booking})


@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'confirmed':
        messages.error(request, 'Cannot edit a confirmed booking')
        return redirect('bookings:booking_list')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Booking updated successfully')
                return redirect('bookings:booking_list')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/booking_edit.html', {'form': form, 'booking': booking})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('bookings:booking_list')
    return redirect('bookings:booking_detail', pk=pk)


@require_POST
@staff_member_required
@csrf_protect
def update_booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid status'})
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})


@require_POST
@csrf_exempt
def verify_qr_code(request):
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')

        booking = Booking.objects.get(
            access_token=access_token,
            status='confirmed',
            date=timezone.now().date()
        )

        booking_start_time = timezone.datetime.strptime(
            booking.time_slot.split('-')[0], '%H:%M').time()
        current_time = timezone.now().time()
        time_diff = timezone.datetime.combine(timezone.now().date(
        ), current_time) - timezone.datetime.combine(timezone.now().date(), booking_start_time)

        if abs(time_diff.total_seconds()) > 1800:  # 30 minutes in seconds
            return JsonResponse({
                'success': False,
                'message': 'Access only allowed 30 minutes before or after booking time'
            })

        return JsonResponse({
            'success': True,
            'booking': {
                'id': booking.id,
                'facility': booking.facility.name,
                'time_slot': booking.time_slot,
                'user': booking.user.username
            }
        })

    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired QR code'
        })
    except Exception as e:
        logger.error(f"Error verifying QR code: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@staff_member_required
def qr_scanner(request):
    return render(request, 'bookings/qr_scanner.html')


@require_POST
@csrf_exempt
def verify_booking(request, booking_data):
    try:
        data = json.loads(booking_data)
        access_token = data.get('access_token')

        # Logic to verify the booking using the access_token
        booking = Booking.objects.get(
            access_token=access_token, status='confirmed')

        # Additional verification logic can go here
        return JsonResponse({
            'success': True,
            'booking': {
                'id': booking.id,
                'facility': booking.facility.name,
                'time_slot': booking.time_slot,
                'user': booking.user.username
            }
        })
    except Booking.DoesNotExist:
        logger.error("Booking not found for access token: %s", access_token)
        return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
    except Exception as e:
        logger.error("Error verifying booking: %s", str(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@csrf_exempt
def verify_qr(request):
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')

        # Logic to verify the booking using the access_token
        booking = Booking.objects.get(
            access_token=access_token, status='confirmed')

        # Additional verification logic can go here
        return JsonResponse({
            'success': True,
            'booking': {
                'id': booking.id,
                'facility': booking.facility.name,
                'time_slot': booking.time_slot,
                'user': booking.user.username
            }
        })
    except Booking.DoesNotExist:
        logger.error("Booking not found for access token: %s", access_token)
        return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
    except Exception as e:
        logger.error("Error verifying booking: %s", str(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
