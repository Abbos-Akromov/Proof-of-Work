from django.shortcuts import render, redirect, get_object_or_404
import secrets
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Profile, Brand, CaseStudy, ProjectImage, ProjectVideo, UserBlockInfo
from .forms import (
    ProfileForm,
    BrandForm,
    CaseStudyForm,
    ProjectImageForm,
    ProjectVideoForm,
    CustomUserCreationForm,
)

ProjectImageFormSet = inlineformset_factory(
    CaseStudy,
    ProjectImage,
    form=ProjectImageForm,
    fields=('image', 'caption'),
    extra=1,
    can_delete=True,
)

ProjectVideoFormSet = inlineformset_factory(
    CaseStudy,
    ProjectVideo,
    form=ProjectVideoForm,
    fields=('video', 'caption'),
    extra=1,
    can_delete=True,
)


def generate_verification_code():
    """6 ta raqamdan iborat tasdiqlash kodi yaratadi."""
    return str(secrets.randbelow(900000) + 100000)


def send_registration_code(email, code):
    subject = "PoW ro'yxatdan o'tish kodi"
    message = (
        "Salom!\n\n"
        "PoW platformaga ro'yxatdan o'tish uchun 6 ta raqamdan iborat kodingiz:\n\n"
        f"  {code}\n\n"
        "Kod 5 daqiqa davomida amal qiladi.\n"
        "Agar siz bu so'rovni amalga oshirmagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring.\n"
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    send_mail(subject, message, from_email, [email], fail_silently=False)


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC VIEWS
# ═══════════════════════════════════════════════════════════════════════════════


def home(request):
    """
    Public home page showing profile, featured brands, and recent case studies.
    Optimized with prefetch_related for minimal database queries.
    """
    profile = Profile.objects.first()

    if not profile:
        return render(request, 'portfolio/home.html', {
            'profile': None,
            'brands_with_studies': [],
            'featured_brands': [],
            'recent_works': [],
            'brand_count': 0,
            'work_count': 0,
        })

    case_study_prefetch = Prefetch(
        'case_studies',
        CaseStudy.objects.filter(is_published=True).prefetch_related('images').order_by('order')
    )

    brands_with_studies = Brand.objects.prefetch_related(
        case_study_prefetch
    ).all().order_by('order')

    all_brands = Brand.objects.all().order_by('-created_at')

    recent_works = CaseStudy.objects.filter(
        is_published=True
    ).select_related('brand').prefetch_related('images').order_by('-created_at')[:12]

    return render(request, 'portfolio/home.html', {
        'profile': profile,
        'brands_with_studies': brands_with_studies,
        'all_brands': all_brands,
        'recent_works': recent_works,
        'brand_count': Brand.objects.count(),
        'work_count': CaseStudy.objects.filter(is_published=True).count(),
    })


def brands(request):
    """Display all brands with their case studies."""
    brands_with_studies = Brand.objects.prefetch_related(
        Prefetch('case_studies', queryset=CaseStudy.objects.filter(is_published=True).prefetch_related('videos'))
    ).all().order_by('order')

    return render(request, 'portfolio/brands.html', {
        'brands': brands_with_studies,
    })


def brand_detail(request, pk):
    """Display a single brand and all its published case studies."""
    brand = get_object_or_404(
        Brand.objects.prefetch_related(
            Prefetch('case_studies', queryset=CaseStudy.objects.filter(is_published=True).prefetch_related('images', 'videos'))
        ),
        pk=pk,
    )

    case_studies = brand.case_studies.filter(is_published=True).prefetch_related('images', 'videos').order_by('order', '-created_at')

    return render(request, 'portfolio/brand_detail.html', {
        'brand': brand,
        'case_studies': case_studies,
    })


def case_study_detail(request, pk):
    """Display detailed view of a single case study."""
    case = get_object_or_404(
        CaseStudy.objects.prefetch_related('images', 'videos'),
        pk=pk,
        is_published=True,
    )

    videos = case.videos.all().order_by('uploaded_at')
    images = case.images.all().order_by('uploaded_at')

    related_works = CaseStudy.objects.filter(
        brand=case.brand,
        is_published=True
    ).exclude(pk=pk).order_by('order')[:3]

    return render(request, 'portfolio/case_study.html', {
        'case': case,
        'related_works': related_works,
        'videos': videos,
        'images': images,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION VIEWS
# ═══════════════════════════════════════════════════════════════════════════════


def custom_register(request):
    """
    Ro'yxatdan o'tish va email orqali kod tasdiqlash jarayoni.
    """
    pending = request.session.get('pending_registration')
    is_verification_step = bool(pending and pending.get('step') == 'verify')
    verification_email = pending.get('email') if pending else None
    username_hint = pending.get('username') if pending else None

    if request.method == 'POST':
        if 'verification_code' in request.POST and pending:
            code = request.POST.get('verification_code', '').strip()
            expires_at = pending.get('expires_at')
            if not code:
                messages.error(request, 'Iltimos, yuborilgan 6 raqamli kodni kiriting.')
            elif timezone.now() > datetime.fromisoformat(expires_at):
                request.session.pop('pending_registration', None)
                messages.error(request, 'Kod muddati tugadi. Yangi kod so‘rang.')
                return redirect('portfolio:custom_register')
            elif code != pending.get('verification_code'):
                messages.error(request, 'Kod noto‘g‘ri. Iltimos, qayta urinib ko‘ring.')
                is_verification_step = True
            else:
                try:
                    username = pending['username']
                    email = pending['email']
                    password = pending['password']

                    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                        messages.error(request, 'Bu login yoki email allaqachon ro‘yxatdan o‘tgan.')
                        request.session.pop('pending_registration', None)
                        return redirect('portfolio:custom_register')

                    User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=False,
                        is_superuser=False,
                        is_active=True,
                    )
                    messages.success(request, 'Foydalanuvchi sifatida muvaffaqiyatli ro‘yxatdan o‘tdingiz.')

                    request.session.pop('pending_registration', None)
                    return redirect('portfolio:custom_login')
                except Exception as e:
                    messages.error(request, f'Xatolik yuz berdi: {str(e)}')
                    request.session.pop('pending_registration', None)
        elif 'resend_code' in request.POST and pending:
            try:
                new_code = generate_verification_code()
                pending['verification_code'] = new_code
                pending['expires_at'] = (timezone.now() + timedelta(minutes=5)).isoformat()
                request.session['pending_registration'] = pending
                send_registration_code(pending['email'], new_code)
                messages.success(request, 'Yangi 6 raqamli kod emailga yuborildi. Iltimos, 5 daqiqa ichida kiriting.')
                is_verification_step = True
                verification_email = pending.get('email')
            except Exception as e:
                messages.error(request, f'Kod yuborishda xatolik: {str(e)}')
                is_verification_step = True
        else:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password1']

                if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                    messages.error(request, 'Bu login yoki email allaqachon ro‘yxatdan o‘tgan.')
                else:
                    try:
                        code = generate_verification_code()
                        request.session['pending_registration'] = {
                            'step': 'verify',
                            'username': username,
                            'email': email,
                            'password': password,
                            'verification_code': code,
                            'expires_at': (timezone.now() + timedelta(minutes=5)).isoformat(),
                        }
                        send_registration_code(email, code)
                        messages.success(request, 'Emailga 6 raqamli kod yuborildi. Iltimos, 5 daqiqa ichida kiriting.')
                        is_verification_step = True
                        verification_email = email
                        username_hint = username
                    except Exception as e:
                        messages.error(request, f'Kod yuborishda xatolik yuz berdi: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    if not is_verification_step:
        form = form if request.method != 'GET' else CustomUserCreationForm()

    return render(request, 'admin_panel/register.html', {
        'form': form,
        'is_verification_step': is_verification_step,
        'verification_email': verification_email,
        'username_hint': username_hint,
    })


def custom_login(request):
    """Login view with authentication."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('portfolio:admin_dashboard')
        return redirect('portfolio:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Foydalanuvchi nomi va parol talab qilinadi.")
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.username}!")
                if user.is_superuser:
                    return redirect('portfolio:admin_dashboard')
                return redirect('portfolio:home')
            else:
                try:
                    existing_user = User.objects.get(username=username)
                    if not existing_user.is_active and existing_user.check_password(password):
                        block_info = getattr(existing_user, 'block_info', None)
                        if block_info and block_info.reason:
                            messages.error(request, f"{block_info.reason} akkountingiz vaqtincha blocklandi")
                        else:
                            messages.error(request, "Akkountingiz vaqtincha bloklandi.")
                    else:
                        messages.error(request, "Parol yoki login xato.")
                except User.DoesNotExist:
                    messages.error(request, "Bunday hisob mavjud emas.")

    return render(request, 'admin_panel/login.html')


def custom_logout(request):
    """Logout user and redirect to home."""
    logout(request)
    messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('portfolio:home')


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD & PROFILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
def admin_dashboard(request):
    """
    Boshqaruv paneli.
    """
    profile = Profile.objects.first()

    if not profile:
        profile = Profile.objects.create(
            name="Ismingiz",
            tagline="Premium Video Editor",
            bio="Professional video editor bio."
        )

    profile_form = ProfileForm(instance=profile)

    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "✓ Profil ma'lumotlari muvaffaqiyatli yangilandi.")
            return redirect('portfolio:admin_dashboard')
        else:
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    brands = Brand.objects.all().order_by('order')
    works = CaseStudy.objects.select_related('brand').order_by('-created_at')

    registered_users = User.objects.all().order_by('-date_joined')

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'brands': brands,
        'works': works,
        'brand_count': brands.count(),
        'work_count': works.count(),
        'registered_users': registered_users,
    }

    return render(request, 'admin_panel/dashboard.html', context)


# ═══════════════════════════════════════════════════════════════════════════════
# BRAND CRUD OPERATIONS
# ═══════════════════════════════════════════════════════════════════════


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
def brand_create(request):
    """Create a new brand."""
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f"✓ '{brand.name}' brand muvaffaqiyatli qo'shildi.")
            return redirect('portfolio:admin_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = BrandForm()

    return render(request, 'admin_panel/brand_form.html', {
        'form': form,
        'action': 'Qo\'shish',
        'page_title': 'Yangi Brand Qo\'shish'
    })


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, f"✓ '{brand.name}' brand muvaffaqiyatli tahrirlandi.")
            return redirect('portfolio:admin_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = BrandForm(instance=brand)

    return render(request, 'admin_panel/brand_form.html', {
        'form': form,
        'action': 'Tahrirlash',
        'page_title': f'"{brand.name}" ni Tahrirlash',
        'brand': brand
    })


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
@require_POST
def brand_delete(request, pk):

    brand = get_object_or_404(Brand, pk=pk)
    brand_name = brand.name
    brand.delete()
    messages.success(request, f"✓ '{brand_name}' brand muvaffaqiyatli o'chirildi.")
    return redirect('portfolio:admin_dashboard')


# ═══════════════════════════════════════════════════════════════════════════════
# CASE STUDY CRUD OPERATIONS
# ═══════════════════════════════════════════════════════════════════════


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
def casestudy_create(request):

    case = CaseStudy()
    if request.method == 'POST':
        form = CaseStudyForm(request.POST, request.FILES, instance=case)
        image_formset = ProjectImageFormSet(
            request.POST,
            request.FILES,
            instance=case,
            prefix='images'
        )
        video_formset = ProjectVideoFormSet(
            request.POST,
            request.FILES,
            instance=case,
            prefix='videos'
        )

        if form.is_valid() and image_formset.is_valid() and video_formset.is_valid():
            case_study = form.save()
            image_formset.instance = case_study
            video_formset.instance = case_study
            image_formset.save()
            video_formset.save()
            messages.success(request, f"✓ '{case_study.title}' ish namunasi muvaffaqiyatli qo'shildi.")
            return redirect('portfolio:admin_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            for formset in (image_formset, video_formset):
                for inline_form in formset:
                    for field, errors in inline_form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
    else:
        form = CaseStudyForm(instance=case)
        image_formset = ProjectImageFormSet(instance=case, prefix='images')
        video_formset = ProjectVideoFormSet(instance=case, prefix='videos')

    return render(request, 'admin_panel/work_form.html', {
        'form': form,
        'image_formset': image_formset,
        'video_formset': video_formset,
        'action': 'Qo\'shish',
        'page_title': 'Yangi Ish Namunasi Qo\'shish'
    })


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
def casestudy_edit(request, pk):
    work = get_object_or_404(CaseStudy, pk=pk)

    if request.method == 'POST':
        form = CaseStudyForm(request.POST, request.FILES, instance=work)
        image_formset = ProjectImageFormSet(
            request.POST,
            request.FILES,
            instance=work,
            prefix='images'
        )
        video_formset = ProjectVideoFormSet(
            request.POST,
            request.FILES,
            instance=work,
            prefix='videos'
        )

        if form.is_valid() and image_formset.is_valid() and video_formset.is_valid():
            case_study = form.save()
            image_formset.instance = case_study
            video_formset.instance = case_study
            image_formset.save()
            video_formset.save()
            messages.success(request, f"✓ '{case_study.title}' ish namunasi muvaffaqiyatli tahrirlandi.")
            return redirect('portfolio:admin_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            for formset in (image_formset, video_formset):
                for inline_form in formset:
                    for field, errors in inline_form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
    else:
        form = CaseStudyForm(instance=work)
        image_formset = ProjectImageFormSet(instance=work, prefix='images')
        video_formset = ProjectVideoFormSet(instance=work, prefix='videos')

    return render(request, 'admin_panel/work_form.html', {
        'form': form,
        'image_formset': image_formset,
        'video_formset': video_formset,
        'action': 'Tahrirlash',
        'page_title': f'"{work.title}" ni Tahrirlash',
        'work': work
    })


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
@require_POST
def casestudy_delete(request, pk):

    work = get_object_or_404(CaseStudy, pk=pk)
    work_title = work.title
    work.delete()
    messages.success(request, f"✓ '{work_title}' ish namunasi muvaffaqiyatli o'chirildi.")
    return redirect('portfolio:admin_dashboard')


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
def api_footer_update(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        profile = Profile.objects.first()
        if not profile:
            return JsonResponse({"status": "error", "message": "Profil topilmadi"}, status=404)

        profile.phone_number = request.POST.get('phone_number', profile.phone_number).strip() if request.POST.get('phone_number') is not None else profile.phone_number
        profile.email = request.POST.get('email', profile.email).strip() if request.POST.get('email') is not None else profile.email
        profile.telegram = request.POST.get('telegram', profile.telegram).strip() if request.POST.get('telegram') is not None else profile.telegram
        profile.instagram = request.POST.get('instagram', profile.instagram).strip() if request.POST.get('instagram') is not None else profile.instagram
        profile.save()

        return JsonResponse({
            "status": "success",
            "phone_number": profile.phone_number,
            "email": profile.email,
            "telegram": profile.telegram,
            "instagram": profile.instagram,
        })
    return JsonResponse({"status": "error", "message": "Noto'g'ri so'rov"}, status=400)


# ═══════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT (block / delete)
# ═══════════════════════════════════════════════════════════════════════════════


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
@require_POST
def user_toggle_active(request, pk):
    """Foydalanuvchini bloklash yoki blokdan chiqarish."""
    target = get_object_or_404(User, pk=pk)

    if target.is_superuser or target == request.user:
        messages.error(request, "Bu foydalanuvchini bloklab bo'lmaydi.")
        return redirect('portfolio:admin_dashboard')

    if target.is_active:
        # Bloklanyapti — sababni saqlaymiz
        reason = request.POST.get('reason', '').strip()
        target.is_active = False
        target.save()
        UserBlockInfo.objects.update_or_create(
            user=target,
            defaults={'reason': reason}
        )
        messages.success(request, f"'{target.username}' bloklandi.")
    else:
        # Blokdan chiqaryapmiz — eski sababni tozalaymiz
        target.is_active = True
        target.save()
        UserBlockInfo.objects.filter(user=target).delete()
        messages.success(request, f"'{target.username}' blokdan chiqarildi.")

    return redirect('portfolio:admin_dashboard')


@user_passes_test(lambda u: u.is_superuser, login_url='portfolio:custom_login')
@require_POST
def user_delete(request, pk):
    """Foydalanuvchini butunlay o'chirish."""
    target = get_object_or_404(User, pk=pk)

    if target.is_superuser or target == request.user:
        messages.error(request, "Bu foydalanuvchini o'chirib bo'lmaydi.")
        return redirect('portfolio:admin_dashboard')

    username = target.username
    target.delete()
    messages.success(request, f"'{username}' o'chirildi.")
    return redirect('portfolio:admin_dashboard')