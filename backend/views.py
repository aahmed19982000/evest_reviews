from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from reviews.models import Review,users , Homepage , ContactMessage
from django.db.models import Count
from reviews.forms import HomepageForm , ContactMessageForm
# Create your views here.
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import StaffUser


def dashboard(request):
    # 1. معالجة طلب الموافقة إذا تم إرسال POST
    if request.method == "POST":
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')
        
        if action == "approve" and review_id:
            review = get_object_or_404(Review, id=review_id)
            review.is_approved = True
            review.save()
            # العودة لنفس صفحة لوحة القيادة بعد التحديث
            return redirect('dashboard')

    # 2. جلب البيانات للعرض (GET)
    pending_reviews = Review.objects.filter(is_approved=False).select_related('user', 'company').order_by('-created_at')[:10]
    
    stats = {
        'total_users': users.objects.count(),
        'total_reviews': Review.objects.count(),
        'pending_count': Review.objects.filter(is_approved=False).count(),
        'approved_count': Review.objects.filter(is_approved=True).count(),
    }
    
    context = {
        'pending_reviews': pending_reviews,
        'stats': stats,
    }
    return render(request, 'backend/dashboard.html', context)



@staff_member_required(login_url='login') 
def manage_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    # --- إضافة الجزء الخاص بالإحصائيات هنا ---
    stats = {
        'total_reviews': reviews.count(),
        'approved_count': reviews.filter(is_approved=True).count(),
    }
    # ---------------------------------------

    if request.method == "POST":
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')
        review = get_object_or_404(Review, id=review_id)
        
        if action == "approve":
            review.is_approved = True
            review.save()
        elif action == "hide":
            review.is_approved = False
            review.save()
        elif action == "delete":
            review.delete()
            
        return redirect('manage_reviews')

    # تأكد من تمرير 'stats' داخل الـ context
    return render(request, 'backend/manage_reviews.html', {
        'reviews': reviews,
        'stats': stats
    })

@staff_member_required(login_url='login')
def manage_users(request):
    # جلب المستخدمين مع حساب عدد المراجعات المرتبطة بكل مستخدم
    all_users = users.objects.all().annotate(reviews_count=Count('reviews')).order_by('-id')
    
    context = {
        'users_list': all_users,
    }
    return render(request, 'backend/manage_users.html', context)

def home(request):
    # جلب أول سجل أو إنشاء واحد افتراضي إذا لم يوجد
    meta_info = Homepage.objects.first()
    
    if request.method == 'POST':
        form = HomepageForm(request.POST, instance=meta_info)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث بيانات الصفحة الرئيسية بنجاح!")
            return redirect('home') # تأكد أن 'home' هو اسم الرابط في urls.py
    else:
        form = HomepageForm(instance=meta_info)

    context = {
        'form': form,
        'meta': meta_info,
    }
    return render(request, 'backend/home.html', context)



@staff_member_required(login_url='login')
def manage_messages(request):
    # جلب جميع الرسائل مرتبة من الأحدث إلى الأقدم
    all_messages = ContactMessage.objects.all().order_by('-created_at')
    
    # اختيار رسالة معينة لعرضها (عند النقر على زر المعاينة)
    selected_message = None
    message_id = request.GET.get('view')
    if message_id:
        selected_message = get_object_or_404(ContactMessage, id=message_id)
        # يمكنك هنا إضافة منطق لتحديد الرسالة كمقروءة إذا أردت

    # معالجة الحذف
    if request.method == "POST" and request.POST.get('action') == 'delete':
        msg_to_delete = get_object_or_404(ContactMessage, id=request.POST.get('message_id'))
        msg_to_delete.delete()
        messages.success(request, "تم حذف الرسالة بنجاح")
        return redirect('manage_messages')

    context = {
        'messages_list': all_messages,
        'selected_message': selected_message,
        'total_count': all_messages.count(),
    }
    return render(request, 'backend/manage_messages.html', context)

from django.views.decorators.csrf import csrf_exempt # تأكد من وجود هذا الاستيراد

@csrf_exempt # غيرناها من csrf_protect لغرض تخطي مشكلة المتصفح
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        u_name = request.POST.get('username') 
        p_pass = request.POST.get('password')
        
        # محاولة التحقق
        user = authenticate(request, username=u_name, password=p_pass)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"مرحباً بك مجدداً {user.username}")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة")
            # أضف هذا السطر لطباعة المحاولة في الـ Terminal عندك للتأكد من وصول البيانات
            print(f"فشل تسجيل الدخول للمستخدم: {u_name}")
    
    return render(request, 'backend/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@staff_member_required(login_url='login')
def manage_staff_member(request, user_id=None):
    instance = get_object_or_404(StaffUser, id=user_id) if user_id else None
    staff_list = StaffUser.objects.all().order_by('-id') # جلب جميع الموظفين
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        # منطق الحذف
        if action == 'delete' and instance:
            username = instance.username
            instance.delete()
            messages.success(request, f"تم حذف الموظف {username} بنجاح")
            return redirect('manage_staff') # تأكد من اسم الرابط في urls.py

        # منطق الإضافة والتعديل
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            if instance:
                instance.username = username
                instance.email = email
                instance.role = role
                instance.is_active = is_active
                if password: instance.set_password(password)
                instance.save()
                messages.success(request, f"تم تحديث بيانات {username}")
            else:
                StaffUser.objects.create_user(
                    username=username, email=email, password=password,
                    role=role, is_active=is_active, is_staff=True
                )
                messages.success(request, "تم إضافة الموظف بنجاح")
            return redirect('manage_staff')
        except Exception as e:
            messages.error(request, f"خطأ: {e}")

    return render(request, 'backend/staff_form.html', {
        'instance': instance,
        'staff_list': staff_list
    })