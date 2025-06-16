from django.shortcuts import render
from facilities.models import Facility

def home(request):
    latest_facilities = Facility.objects.all().order_by('-id')[:3]
    return render(request, 'home.html', {'latest_facilities': latest_facilities}) 