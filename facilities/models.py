from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    operating_hours = models.CharField(max_length=100)
    image = models.ImageField(upload_to='facility_images/', blank=True, null=True)

    def __str__(self):
        return self.name
