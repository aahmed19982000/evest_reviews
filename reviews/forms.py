from django import forms
from .models import Homepage , ContactMessage

class HomepageForm(forms.ModelForm):
    class Meta:
        model = Homepage
        fields = ['meta_title', 'meta_description']
        widgets = {
            'meta_title': forms.TextInput(attrs={
                'class': 'form-input w-full bg-background-dark border-border-dark text-white rounded-lg p-3 focus:ring-primary',
                'placeholder': 'أدخل عنوان الميتا هنا...'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-input w-full bg-background-dark border-border-dark text-white rounded-lg p-3 focus:ring-primary h-32',
                'placeholder': 'أدخل وصف الميتا هنا...'
            }),
        }

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full bg-background-dark border-border-dark text-white rounded-lg p-3 focus:ring-primary',
                'placeholder': 'أدخل اسمك...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full bg-background-dark border-border-dark text-white rounded-lg p-3 focus:ring-primary',
                'placeholder': 'أدخل بريدك الإلكتروني...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input w-full bg-background-dark border-border-dark text-white rounded-lg p-3 focus:ring-primary h-32',
                'placeholder': 'اكتب رسالتك هنا...'
            }),
        }