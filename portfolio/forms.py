from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Brand, CaseStudy, ProjectImage, ProjectVideo


class TailwindFormMixin:
    """Inject premium Tailwind CSS styling into all form fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_class = field.widget.attrs.get('class', '')
            
            if isinstance(field.widget, forms.CheckboxInput):
                classes = "w-5 h-5 rounded text-amber-500 bg-zinc-900 border-zinc-700 focus:ring-amber-500 focus:ring-offset-0 focus:outline-none transition cursor-pointer"
            elif isinstance(field.widget, (forms.FileInput, forms.ClearableFileInput)):
                classes = (
                    "block w-full text-sm text-zinc-400 file:mr-4 file:py-2 file:px-4 file:rounded-md "
                    "file:border-0 file:text-xs file:font-bold file:uppercase file:bg-amber-500/20 "
                    "file:text-amber-400 hover:file:bg-amber-500/30 file:cursor-pointer transition"
                )
            elif isinstance(field.widget, forms.Textarea):
                classes = (
                    "w-full px-4 py-3 rounded-lg border bg-zinc-900 border-zinc-700 text-white "
                    "placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-amber-500 "
                    "focus:border-amber-500 transition duration-200 resize-none"
                )
            elif isinstance(field.widget, forms.Select):
                classes = (
                    "w-full px-4 py-3 rounded-lg border bg-zinc-900 border-zinc-700 text-white "
                    "focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 "
                    "transition duration-200 cursor-pointer"
                )
            else:
                classes = (
                    "w-full px-4 py-3 rounded-lg border bg-zinc-900 border-zinc-700 text-white "
                    "placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-amber-500 "
                    "focus:border-amber-500 transition duration-200"
                )
                
            field.widget.attrs['class'] = f"{existing_class} {classes}".strip()


class ProfileForm(TailwindFormMixin, forms.ModelForm):
    """Edit profile information with premium Tailwind styling."""

    class Meta:
        model = Profile
        fields = [
            'name', 'tagline', 'bio', 'avatar', 'years_experience', 'skills',
            'phone_number', 'email', 'instagram', 'telegram', 'youtube', 'linkedin',  # <-- phone_number qo'shildi
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Sizning haqingizda qisqacha malumot...'}),
            'skills': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Premiere Pro, After Effects, DaVinci Resolve, Motion Graphics'}),
            'tagline': forms.TextInput(attrs={'placeholder': 'Video Editor · Content Creator · Motion Specialist'}),
            'name': forms.TextInput(attrs={'placeholder': 'To\'liq isminiz'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'}),  # <-- widget qo'shildi
            'email': forms.EmailInput(attrs={'placeholder': 'example@email.com'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://instagram.com/username'}),
            'telegram': forms.URLInput(attrs={'placeholder': 'https://t.me/username'}),
            'youtube': forms.URLInput(attrs={'placeholder': 'https://youtube.com/@username'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}),
            'years_experience': forms.NumberInput(attrs={'placeholder': '5', 'min': '0'}),
        }


class BrandForm(TailwindFormMixin, forms.ModelForm):
    """Create/Edit brand with premium styling."""
    
    class Meta:
        model = Brand
        fields = [
            'name', 'logo', 'category', 'work_label', 'description', 'website', 'is_featured', 'order',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Brand yoki kliyent nomi'}),
            'work_label': forms.TextInput(attrs={'placeholder': 'Masalan: YouTube kampaniyasi uchun video montaj'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brand haqida qisqacha tavsif...'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://brand-website.com'}),
            'order': forms.NumberInput(attrs={'placeholder': '0', 'min': '0'}),
        }



class ProjectImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Rasm uchun qisqacha yozuv (ixtiyoriy)'}),
        }


class ProjectVideoForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectVideo
        fields = ['video', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Video uchun qisqacha yozuv (ixtiyoriy)'}),
        }


class CaseStudyForm(TailwindFormMixin, forms.ModelForm):
    """Create/Edit case study with premium styling."""
    
    class Meta:
        model = CaseStudy
        fields = [
            'brand', 'title', 'project_year', 'description',
            'thumbnail', 'tags', 'is_published', 'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Video loyihaning nomi'}),
            'project_year': forms.NumberInput(attrs={'placeholder': '2025', 'min': '1900', 'max': '2100'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Bu loyihada nima qilgan bolasiz?'}),
            'tags': forms.TextInput(attrs={'placeholder': 'montaj, animatsiya, rang korektsiyasi'}),
            'order': forms.NumberInput(attrs={'placeholder': '1', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['project_year'].required = True
        self.fields['description'].required = True


class CustomUserCreationForm(TailwindFormMixin, UserCreationForm):
    """User registration form with single-user security check."""
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Foydalanuvchi nomi'
        self.fields['email'].widget.attrs['placeholder'] = 'Email manzili'
        self.fields['password1'].widget.attrs['placeholder'] = 'Parol'
        self.fields['password2'].widget.attrs['placeholder'] = 'Parolni tasdiqlang'
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu email manzili allaqachon ro\'yxatdan o\'tgan.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu foydalanuvchi nomi allaqachon mavjud.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Kiritilgan parollar bir-biriga mos kelmadi.')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError('Parol kamida 8 belgida iborat bo\'lishi kerak.')
        return password2
