from django.db import models
from django.contrib.auth.models import AbstractUser

class StaffUser(AbstractUser):
    # تعريف الأدوار (Roles) للموظفين
    ROLE_CHOICES = (
        ('admin', 'مدير نظام'),
        ('moderator', 'مراقب تقييمات'),
        ('support', 'دعم فني'),
    )
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='moderator', 
        verbose_name="الصلاحية"
    )
    
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="رقم الجوال"
    )
    
    profile_picture = models.ImageField(
        upload_to='staff_photos/', 
        blank=True, 
        null=True, 
        verbose_name="الصورة الشخصية"
    )

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"