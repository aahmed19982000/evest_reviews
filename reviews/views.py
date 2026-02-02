from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Company, Review, Homepage  , users  , TypeOfExperience
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from django.db.models import Q , Count

def home(request):
    company = Company.objects.first()
    meta_info = Homepage.objects.first()
    
    all_reviews = Review.objects.filter(company=company).order_by('-created_at') if company else Review.objects.none()
    total_count = all_reviews.count()
    
    average_data = all_reviews.aggregate(Avg('rating'))
    rating_avg = average_data['rating__avg'] or 0
    
    star_stats = []
    for i in range(5, 0, -1):
        count = all_reviews.filter(rating=i).count()
        percentage = (count / total_count * 100) if total_count > 0 else 0
        star_stats.append({
            'star': i,
            'count': count,
            'percentage': int(percentage)
        })

    # --- الجزء المطلوب إضافته هنا لـ "أكثر الشكاوى شيوعاً" ---
    
    # 1. جلب أنواع الشكاوى من المراجعات التي تم تعليمها كـ "مشكلة"
    common_complaints = all_reviews.filter(is_problematic=True, experience_type_dynamic__isnull=False) \
        .values('experience_type_dynamic__name') \
        .annotate(count=Count('experience_type_dynamic')) \
        .order_by('-count')[:3] # جلب أعلى 3 شكاوى تكراراً

    # 2. حساب إجمالي عدد المشاكل لحساب النسبة المئوية لكل واحدة
    total_problems = all_reviews.filter(is_problematic=True).count()
    
    complaints_data = []
    for complaint in common_complaints:
        # حساب نسبة كل شكوى من إجمالي المشاكل
        p_ratio = (complaint['count'] / total_problems * 100) if total_problems > 0 else 0
        complaints_data.append({
            'name': complaint['experience_type_dynamic__name'],
            'percentage': round(p_ratio, 1)
        })
    # -------------------------------------------------------

    context = {
        'company': company,
        'meta': meta_info,
        'reviews': all_reviews,
        'rating_avg': round(rating_avg, 1),
        'total_count': total_count,
        'star_stats': star_stats,
        'complaints_data': complaints_data, # أضف هذا المتغير للسياق
    }
    return render(request, 'reviews/index.html', context)

def get_client_ip(request):
    """وظيفة لجلب عنوان IP الخاص بالمستخدم"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_country(ip_address):
    """وظيفة لجلب اسم البلد بناءً على الـ IP"""
    try:
        # استخدام API مجاني لجلب بيانات الموقع
        response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        return response.get('country_name', 'غير محدد')
    except:
        return "غير محدد"



def submit_review(request, slug):
    company = Company.objects.first()
    # جلب جميع أنواع التجارب لعرضها في القائمة المنسدلة
    experience_types = TypeOfExperience.objects.all()
    
    if request.method == 'POST':
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        user_mobile = request.POST.get('mobile')
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        # جلب القيمة المختارة من القائمة
        experience_type_id = request.POST.get('experience_type')
        # جلب القيمة المكتوبة في حال اختار "أخرى"
        other_reason = request.POST.get('other_reason') 
        media = request.FILES.get('media')

        # منطق الربط الذكي للمستخدم
        user_obj = users.objects.filter(Q(email=user_email) | Q(mobile=user_mobile)).first()

        if user_obj:
            updated = False
            if user_email and user_obj.email != user_email:
                user_obj.email = user_email
                updated = True
            if user_mobile and user_obj.mobile != user_mobile:
                user_obj.mobile = user_mobile
                updated = True
            if updated: user_obj.save()
        else:
            user_obj = users.objects.create(name=user_name, email=user_email, mobile=user_mobile)

        user_ip = get_client_ip(request)
        user_country = get_user_country(user_ip)

        try:
            # تحديد نوع التجربة للموديل (ForeignKey)
            exp_obj = None
            if experience_type_id and experience_type_id != "other":
                exp_obj = TypeOfExperience.objects.get(id=experience_type_id)

            # --- التعديل المستهدف هنا فقط ---
            # تم إضافة "خدمة العملاء" وفحص اسم النوع المختار بشكل أكثر مرونة
            is_problem = False
            if experience_type_id == "other" and other_reason:
                is_problem = True
            elif exp_obj:
                # الكلمات التي تعتبر بلاغاً عن مشكلة
                issue_keywords = ["سحب", "خدمة العملاء", "دعم", "تأخير", "منصة"]
                if any(word in exp_obj.name for word in issue_keywords):
                    is_problem = True

            # إنشاء المراجعة
            new_review = Review.objects.create(
                company=company,
                user=user_obj,
                rating=int(rating),
                comment=comment,
                country=user_country,
                experience_type_dynamic=exp_obj, 
                is_problematic=is_problem, # تم استبدال المنطق القديم بالمتغير الجديد
                media=media
            )
            # -------------------------------
            
            user_obj.reviews.add(new_review)
            messages.success(request, "تم إضافة تقييمك بنجاح!")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"حدث خطأ: {e}")

    return render(request, 'reviews/submit_review.html', {
        'company': company,
        'experience_types': experience_types # إرسال الأنواع للقالب
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
    user_info = get_object_or_404(users, id=user_id)
    # جلب جميع المراجعات المرتبطة بهذا المستخدم
    user_reviews = user_info.reviews.all().order_by('-created_at')
    
    return render(request, 'reviews/user_profile.html', {
        'profile_user': user_info,
        'user_reviews': user_reviews
    })