from django.contrib import admin
from .models import CustomUser, UserProfile




class CustomUserAmin(admin.ModelAdmin):
    list_display = ("phone_number", "id", "first_name", "last_name", "email_address", 'gender',)
    list_filter = ("phone_number",)
    search_fields = ("phone_number",)



admin.site.register(CustomUser, CustomUserAmin)

admin.site.register(UserProfile)

