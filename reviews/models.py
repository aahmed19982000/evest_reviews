from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models
from django.utils.text import slugify
from PIL import Image
import io
from django.core.files.base import ContentFile


class Company(models.Model):
    # المعلومات الأساسية
    name = models.CharField(max_length=100, default="Evest")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="وصف المنصة تحت العنوان")
    
    # تفاصيل التسجيل (البطاقات الثلاث في المنتصف)
    license = models.CharField(max_length=100, verbose_name="الترخيص") # VFSC 17910
    regulator = models.CharField(max_length=100, verbose_name="جهة التنظيم") # هيئة الخدمات المالية
    country = models.CharField(max_length=100, verbose_name="بلد التسجيل") # جمهورية فانواتو
    
    # قسم تنبيه المخاطر (المربع الأحمر)
    risk_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان التنبيه")
    risk_message = models.TextField(blank=True, verbose_name="رسالة التحذير")
    risk_link = models.URLField(blank=True, verbose_name="رابط (اقرأ المزيد)")
    is_risk_active = models.BooleanField(default=False, verbose_name="تفعيل التنبيه")

    # ملخص الإيجابيات والسلبيات (Sidebar)
    # ملاحظة: يمكن عملها كجدول منفصل، ولكن للتبسيط لشركة واحدة سنستخدم TextField مع فواصل
    pros = models.TextField(help_text="أدخل كل ميزة في سطر منفصل", verbose_name="الإيجابيات")
    cons = models.TextField(help_text="أدخل كل عيب في سطر منفصل", verbose_name="السلبيات")

    # أكثر الشكاوي شيوعاً (النسب المئوية في Sidebar)
    withdrawal_delay_percent = models.IntegerField(default=0, verbose_name="نسبة تأخر السحب")
    technical_support_percent = models.IntegerField(default=0, verbose_name="نسبة دعم فني")
    slippage_percent = models.IntegerField(default=0, verbose_name="نسبة انزلاقات سعرية")

    # روابط التواصل/الموقع (Buttons)
    website_url = models.URLField(blank=True, verbose_name="رابط الموقع الرسمي")
    is_independent = models.BooleanField(default=True, verbose_name="موقع مستقل وغير تابع")
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "بيانات الشركة"
        verbose_name_plural = "بيانات الشركة"
    


class users(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15,)
    reviews=models.ManyToManyField('Review', related_name='user_reviews', blank=True)
    country = models.CharField(max_length=100, verbose_name="البلد", blank=True, null=True)

    def __str__(self):
        return self.name
    
class TypeOfExperience(models.Model):
    name = models.CharField(max_length=100, verbose_name="نوع التجربة")

    def __str__(self):
        return self.name

class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews', verbose_name="الشركة", null=True, blank=True)
    user = models.ForeignKey(users, on_delete=models.CASCADE, related_name='my_reviews', verbose_name="المستخدم")
    
    experience_type_dynamic = models.ForeignKey(
        'TypeOfExperience', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="نوع التجربة"
    )
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="التقييم (1-5)")
    comment = models.TextField(verbose_name="التعليق")
    country = models.CharField(max_length=100, verbose_name="البلد")
    is_problematic = models.BooleanField(default=False, verbose_name="بلاغ عن مشكلة") 
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='review_media/', blank=True, null=True, verbose_name="وسائط المراجعة")
    is_approved = models.BooleanField(default=False, verbose_name="تمت الموافقة")

    def __str__(self):
        return f"{self.user.name} - {self.rating} Stars"
    
    

    # --- أضف هذه الدالة لضغط الصور تلقائياً قبل الحفظ ---
    def save(self, *args, **kwargs):
        if self.media:
            # فتح الصورة
            img = Image.open(self.media)
            
            # التأكد من تحويل الصور (مثل PNG الشفاف) إلى صيغة RGB لتقليل الحجم
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # ضبط الأبعاد القصوى (مثلاً 1000 بكسل عرض) مع الحفاظ على التناسب
            max_size = (1000, 1000)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # حفظ الصورة في الذاكرة بضغط 70%
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=70) 
            output.seek(0)

            # استبدال الملف المرفوع بالملف المضغوط
            # نقوم بتغيير الامتداد إلى .jpg لضمان أقل حجم ممكن
            new_name = f"{self.media.name.split('.')[0]}.jpg"
            self.media = ContentFile(output.read(), name=new_name)

        super().save(*args, **kwargs)  

class ReviewReply(models.Model):
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    # أضف null=True و blank=True هنا
    user = models.ForeignKey(users, on_delete=models.CASCADE, related_name='user_replies', null=True, blank=True)
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "رد مستخدم"
        verbose_name_plural = "ردود المستخدمين"

    def __str__(self):
        return f"رد من {self.user.name} على {self.review.user.name}"
    

class Homepage(models.Model):
    meta_title = models.CharField(max_length=200, verbose_name="عنوان الميتا")
    meta_description = models.TextField(verbose_name="وصف الميتا")

    def __str__(self):
        return "Homepage Meta Information"
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="الاسم")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    message = models.TextField(verbose_name="الرسالة")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"رسالة من {self.name} - {self.subject}"