from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Facility
from bookings.forms import BookingForm
from django.http import JsonResponse
from bookings.models import Booking
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError

@login_required
def facility_list(request):
    query = request.GET.get('q', '')
    if query:
        facilities = Facility.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    else:
        facilities = Facility.objects.all()
    return render(request, 'facilities/facility_list.html', {'facilities': facilities})

@login_required
def facility_detail(request, id):
    facility = get_object_or_404(Facility, id=id)
    bookings = Booking.objects.filter(facility=facility).order_by('date', 'time_slot')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, facility=facility)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.facility = facility
            
            try:
                # Check if the time slot is already booked
                existing_booking = Booking.objects.filter(
                    facility=facility,
                    date=form.cleaned_data['date'],
                    time_slot=form.cleaned_data['time_slot']
                ).exists()
                
                if existing_booking:
                    messages.error(request, 'This time slot is already booked. Please select another time.')
                else:
                    booking.save()
                    messages.success(request, 'Booking confirmed successfully!')
                    return redirect('bookings:booking_confirmation', booking_id=booking.id)
                    
            except IntegrityError:
                messages.error(request, 'This time slot is already booked. Please select another time.')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = BookingForm(facility=facility)

    context = {
        'facility': facility,
        'form': form,
        'bookings': bookings
    }
    return render(request, 'facilities/facility_detail.html', context)

def facility_search(request):
    query = request.GET.get('q', '')
    if query:
        facilities = Facility.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    else:
        facilities = Facility.objects.all()
    return render(request, 'facilities/facility_list.html', {'facilities': facilities})

def check_availability(request):
    facility_id = request.GET.get('facility_id')
    date = request.GET.get('date')
    time_slot = request.GET.get('time_slot')
    
    if not all([facility_id, date, time_slot]):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    try:
        facility = Facility.objects.get(id=facility_id)
        is_available = not Booking.objects.filter(
            facility=facility,
            date=date,
            time_slot=time_slot
        ).exists()
        
        return JsonResponse({
            'available': is_available,
            'facility_name': facility.name,
            'date': date,
            'time_slot': time_slot
        })
    except Facility.DoesNotExist:
        return JsonResponse({'error': 'Facility not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
