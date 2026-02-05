from django.contrib import admin
from .models import StaffUser

# Register your models here.

admin.site.register(StaffUser) 
class StaffUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone_number')
    search_fields = ('username', 'email', 'role')
    list_filter = ('role',)