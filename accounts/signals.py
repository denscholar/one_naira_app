from django.db.models.signals import post_save
from accounts.models import CustomUser
from django.dispatch import receiver
from .models import UserProfile

# signal to create a wallet when a new CustomUser is created
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
    # Save the profile when the user is saved
    instance.profile.save()