from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 

# 1. استيراد أداة الـ sitemap من دجانغو
from django.contrib.sitemaps import views as sitemap_views # استيراد العروض
from reviews.sitemaps import ReviewSitemap, UserSitemap

sitemaps = {
    'review': ReviewSitemap,
    'users': UserSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reviews.urls')),
    
    # 1. رابط الفهرس الرئيسي (Index)
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    
    # 2. رابط الخرائط الفرعية (سيتولد تلقائياً روابط مثل sitemap-companies.xml)
    path('sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps}, 
         name='django.contrib.sitemaps.views.sitemap'),
]