from django import forms
from .models import Booking
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time_slot']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.facility = kwargs.pop('facility', None)
        super().__init__(*args, **kwargs)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError("Please select a date.")
        if date < datetime.now().date():
            raise forms.ValidationError("Cannot book dates in the past")
        if date > datetime.now().date() + timedelta(days=30):
            raise forms.ValidationError("Cannot book more than 30 days in advance")
        return date 