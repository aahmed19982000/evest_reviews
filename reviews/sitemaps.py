from django.contrib.sitemaps import Sitemap
from .models import Company, users , Review
class ReviewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Review.objects.all()

    def location(self, obj):
        return f'/Review/{obj.id}/'

# تأكد من وجود هذا الكلاس تحديداً بنفس هذا الاسم
class UserSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return users.objects.all()

    def location(self, obj):
        # تأكد أن الرابط يطابق مسار صفحة المستخدم عندك
        return f'/user/{obj.id}/'