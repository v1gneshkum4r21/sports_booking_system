from django.db import models
from django.contrib.auth import get_user_model
from facilities.models import Facility
from django.core.exceptions import ValidationError
from datetime import datetime
import qrcode
from io import BytesIO
from django.core.files import File
import uuid
import json
from django.utils import timezone

class Booking(models.Model):
    TIME_SLOTS = [
        ('09:00-10:00', '9 AM - 10 AM'),
        ('10:00-11:00', '10 AM - 11 AM'),
        ('11:00-12:00', '11 AM - 12 PM'),
        ('12:00-13:00', '12 PM - 1 PM'),
        ('13:00-14:00', '1 PM - 2 PM'),
        ('14:00-15:00', '2 PM - 3 PM'),
        ('15:00-16:00', '3 PM - 4 PM'),
        ('16:00-17:00', '4 PM - 5 PM'),
        ('17:00-18:00', '5 PM - 6 PM'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=50, choices=TIME_SLOTS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    access_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='booking_qrcodes/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['facility', 'date', 'time_slot']
        ordering = ['date', 'time_slot']

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        data = {
            'access_token': str(self.access_token)
        }
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_code_{self.id}.png'
        
        self.qr_code.save(filename, File(buffer), save=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if self.status == 'confirmed' and not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=['access_token', 'qr_code'])

    def clean(self):
        if self.date and self.date < datetime.now().date():
            raise ValidationError('Cannot book for past dates')
        
        if hasattr(self, 'facility') and self.date and self.time_slot:
            conflicts = Booking.objects.filter(
                facility=self.facility,
                date=self.date,
                time_slot=self.time_slot,
                status='confirmed'
            ).exclude(id=self.id)
            
            if conflicts.exists():
                raise ValidationError('This time slot is already booked')

    def __str__(self):
        return f"{self.user} - {self.facility} on {self.date} at {self.time_slot}"

    def generate_qr_data(self):
        return json.dumps({
            'access_token': str(self.access_token)
        })

    def verify(self):
        """Mark the booking as verified and set the verified timestamp."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
