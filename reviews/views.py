from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Company, Review, Homepage  , users  , TypeOfExperience , ReviewReply
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from django.db.models import Q , Count , Max

def home(request):
    # 1. جلب البيانات الأساسية للشركة والميتا
    company = Company.objects.first()
    meta_info = Homepage.objects.first()
    
    # 2. جلب المراجعات الأساسية المرتبطة بهذه الشركة
    base_reviews = Review.objects.filter(company=company) if company else Review.objects.none()

    # 3. تصفية المراجعات: جلب أحدث مراجعة فقط لكل مستخدم (لمنع التكرار)
    # أولاً: نحسب قائمة الـ IDs لأحدث المراجعات
    latest_review_ids = base_reviews.values('user').annotate(max_id=Max('id')).values_list('max_id', flat=True)
    
    # ثانياً: جلب المراجعات الفعلية مع الردود (select_related) ونوع التجربة (prefetch_related) لتقليل الاستعلامات
    unique_reviews = Review.objects.filter(id__in=latest_review_ids)\
    .select_related('user', 'company', 'experience_type_dynamic')\
    .prefetch_related('replies__user')\
    .order_by('-created_at')

    # 4. الحسابات الإحصائية للنجوم
    total_count = base_reviews.count()
    average_data = base_reviews.aggregate(Avg('rating'))
    rating_avg = average_data['rating__avg'] or 0
    
    star_stats = []
    for i in range(5, 0, -1):
        count = base_reviews.filter(rating=i).count()
        percentage = (count / total_count * 100) if total_count > 0 else 0
        star_stats.append({
            'star': i,
            'count': count,
            'percentage': int(percentage)
        })

    # 5. حساب الشكاوى الشائعة بناءً على "بلاغات المشاكل"
    common_complaints = base_reviews.filter(is_problematic=True, experience_type_dynamic__isnull=False) \
        .values('experience_type_dynamic__name') \
        .annotate(count=Count('experience_type_dynamic')) \
        .order_by('-count')[:3]

    total_problems = base_reviews.filter(is_problematic=True).count()
    
    complaints_data = []
    for complaint in common_complaints:
        p_ratio = (complaint['count'] / total_problems * 100) if total_problems > 0 else 0
        complaints_data.append({
            'name': complaint['experience_type_dynamic__name'],
            'percentage': round(p_ratio, 1)
        })

    # 6. تجهيز السياق للقالب
    context = {
        'company': company,
        'meta': meta_info,
        'reviews': unique_reviews,
        'rating_avg': round(rating_avg, 1),
        'total_count': total_count,
        'star_stats': star_stats,
        'complaints_data': complaints_data,
    }
    return render(request, 'reviews/index.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_country(ip_address):
    # إذا كان الجهاز محلي، لن نجد دولة
    if ip_address == '127.0.0.1':
        return "جهاز محلي (Localhost)"
    
    try:
        # استخدام خدمة ip-api المجانية
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        data = response.json()
        if data['status'] == 'success':
            return data['country'] 
    except:
        pass
    return " السعودية"


def submit_review(request, slug):
    company = Company.objects.first()
    experience_types = TypeOfExperience.objects.all()
    
    if request.method == 'POST':
        # ... (نفس الكود الخاص بجلب البيانات من POST)
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        user_mobile = request.POST.get('mobile')
        rating = request.POST.get('rating', 1) # الافتراضي 1
        comment = request.POST.get('comment')
        experience_type_id = request.POST.get('experience_type')
        other_reason = request.POST.get('other_reason') 
        
        # التأكد من جلب الملف المرفوع
        media = request.FILES.get('media')

        # منطق جلب الـ IP الحقيقي والبلد آلياً
        user_ip = get_client_ip(request)
        
        # --- حل مشكلة البلد آلياً ---
        user_country = "غير معروف"
        if user_ip != '127.0.0.1': # إذا لم يكن الجهاز محلياً
            try:
                # طلب سريع لخدمة الـ IP لجلب اسم البلد
                response = requests.get(f'http://ip-api.com/json/{user_ip}', timeout=2)
                data = response.json()
                if data.get('status') == 'success':
                    user_country = data.get('country')
            except:
                user_country = "فشل التعرف"
        else:
            user_country = "السعودية" # قيمة للتجربة فقط على جهازك
        # ---------------------------

        # ... (نفس منطق المستخدم)
        user_obj, created = users.objects.get_or_create(
            email=user_email, 
            defaults={'name': user_name, 'mobile': user_mobile}
        )

        try:
            exp_obj = None
            if experience_type_id and experience_type_id != "other":
                exp_obj = TypeOfExperience.objects.get(id=experience_type_id)

            # منطق تحديد المشكلة (الذي أضفناه سابقاً)
            is_problem = False
            if experience_type_id == "other" and other_reason:
                is_problem = True
            elif exp_obj:
                issue_keywords = ["سحب", "خدمة العملاء", "دعم", "تأخير", "منصة"]
                if any(word in exp_obj.name for word in issue_keywords):
                    is_problem = True

            # إنشاء المراجعة (هنا يتم حفظ البلد والمديا)
            new_review = Review.objects.create(
                company=company,
                user=user_obj,
                rating=int(rating),
                comment=comment,
                country=user_country, # سيتم حفظ البلد المجلوب آلياً
                experience_type_dynamic=exp_obj, 
                is_problematic=is_problem,
                media=media # سيتم حفظ الملف في مجلد review_media الموحد
            )
            
            messages.success(request, "تم إضافة تقييمك بنجاح!")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"حدث خطأ: {e}")

    return render(request, 'reviews/submit_review.html', {
        'company': company,
        'experience_types': experience_types
    })

def review_detail(request, review_id):
    # جلب المراجعة أو إظهار 404 إذا لم تكن موجودة
    review = get_object_or_404(Review, id=review_id)
    
    context = {
        'review': review,
        'company': review.company, # جلب الشركة المرتبطة بالمراجعة
    }
    return render(request, 'reviews/review_single.html', context)

def user_profile(request, user_id):
    profile_user = get_object_or_404(users, id=user_id)
    
    # التعديل هنا: احذف 'reply' من select_related وأضف prefetch_related('replies__user')
    user_reviews = Review.objects.filter(user=profile_user)\
        .select_related('company', 'experience_type_dynamic')\
        .prefetch_related('replies__user')\
        .order_by('-created_at')

    # تأكد من وجود هذا المنطق لمعرفة ما إذا كان هناك صور (Media)
    has_media = user_reviews.exclude(media='').exists()

    context = {
        'profile_user': profile_user,
        'user_reviews': user_reviews,
        'has_media': has_media,
    }
    return render(request, 'reviews/user_profile.html', context)

def add_reply(request):
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        reply_text = request.POST.get('reply_text')
        
        # بيانات المستخدم من الفورم
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        user_mobile = request.POST.get('mobile')

        # 1. البحث عن المراجعة الأصلية
        review_obj = get_object_or_404(Review, id=review_id)

        # 2. تطبيق منطق get_or_create للمستخدم
        user_obj, created = users.objects.get_or_create(
            email=user_email,
            defaults={'name': user_name, 'mobile': user_mobile}
        )

        # 3. إنشاء الرد وربطه بالمستخدم والمراجعة
        try:
            ReviewReply.objects.create(
                review=review_obj,
                user=user_obj,
                reply_text=reply_text
            )
            messages.success(request, "تم إضافة ردك بنجاح!")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة الرد: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'home'))