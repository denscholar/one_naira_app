from django.contrib import admin
from .models import ContactUs


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'isSubscribe', 'created_at',)
    list_display_links = ('name',)
    search_fields = ('name', 'email', 'created_at',)

    
admin.site.register(ContactUs, ContactAdmin)
