from django.contrib import admin

# Register your models here.
from .models import Company, users, Review , Homepage , TypeOfExperience

admin.site.register(Company)
class usersAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


admin.site.register(users)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
    search_fields = ('user__name', 'user__email')
    list_filter = ('rating',)


admin.site.register(Review) 
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'license', 'regulator', 'country', 'is_risk_active')
    search_fields = ('name', 'license', 'regulator', 'country')
    list_filter = ('is_risk_active',)

admin.site.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    list_display = ('meta_title',)
    search_fields = ('meta_title',)

admin.site.register(TypeOfExperience)
class TypeOfExperienceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)