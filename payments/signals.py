from django.db.models.signals import post_save
from accounts.models import CustomUser
from django.dispatch import receiver
from .models import Wallet

# signal to create a wallet when a new CustomUser is created
@receiver(post_save, sender=CustomUser)
def save_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        
    # Save the wallet when the user is saved
    instance.wallet.save()
