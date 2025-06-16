from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    # Add additional fields if needed
    pass

    class Meta:
        db_table = 'auth_user'

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    registration_number = models.CharField(max_length=20, unique=False, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    # Add other fields as needed

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'registration_number': '',
                'course': '',
                'year_of_study': None,
                'phone': ''
            }
        )
    else:
        Profile.objects.get_or_create(user=instance)
        if hasattr(instance, 'profile'):
            instance.profile.save()
