from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 
from django.http import HttpResponse
from django.contrib.sitemaps import views as sitemap_views
from reviews.sitemaps import ReviewSitemap, UserSitemap

# 1. تعريف الخرائط
sitemaps = {
    'review': ReviewSitemap,
    'users': UserSitemap,
}

# 2. دالة robots.txt (يفضل وضعها قبل urlpatterns)
def robots_txt(request):
    content = (
        "Sitemap: https://evestreviews.pythonanywhere.com/sitemap.xml\n\n"
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
    )
    return HttpResponse(content, content_type="text/plain")

# 3. قائمة روابط واحدة لكل شيء
urlpatterns = [
    path('admin-panel/', admin.site.urls), # لوحة تحكم Django الأساسية (Jazzmin)
    
    path('', include('reviews.urls')), 
    
    # هذا الرابط يشير إلى تطبيقك المخصص (Custom Backend) الذي برمجت فيه الـ Dashboard
    path('backend/', include('backend.urls')),
    
    # روابط الخرائط
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path('sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # رابط robots.txt
    path("robots.txt", robots_txt), 
]
# إضافة روابط الملفات الثابتة
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)