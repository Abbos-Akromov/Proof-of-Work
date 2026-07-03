from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Profile(models.Model):
    """Owner profile — only one row ever exists (singleton)."""
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200, blank=True)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True)
    years_experience = models.PositiveIntegerField(default=0)

    # Contact and Social links
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="+998 99 999 99 99")
    email = models.EmailField(blank=True)
    instagram = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    # Skills stored as comma-separated string for simplicity
    skills = models.TextField(
        blank=True,
        help_text="Vergul bilan ajrating: Premiere Pro, After Effects, DaVinci Resolve"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profil'

    def __str__(self):
        return self.name

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]


class Brand(models.Model):
    """A brand / client the editor has worked with."""
    CATEGORY_CHOICES = [
        ('youtube', 'YouTube'),
        ('commercial', 'Reklama'),
        ('music', 'Musiqa videosi'),
        ('documentary', 'Hujjatli film'),
        ('social', 'Ijtimoiy tarmoq'),
        ('other', 'Boshqa'),
    ]

    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    # Short label shown directly under the logo on the public page
    work_label = models.CharField(
        max_length=200,
        help_text="Masalan: YouTube kampaniyasi uchun video montaj"
    )
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Kichik raqam = birinchi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brandlar'

    def __str__(self):
        return self.name

    @property
    def top_work(self):
        return self.case_studies.filter(is_published=True).first()

    @property
    def latest_video(self):
        # Prefer prefetched case studies and videos when available.
        if hasattr(self, '_prefetched_objects_cache') and 'case_studies' in self._prefetched_objects_cache:
            videos = []
            for case in self.case_studies.all():
                videos.extend(list(case.videos.all()))
            if videos:
                return max(videos, key=lambda v: v.uploaded_at or v.pk)

        return ProjectVideo.objects.filter(
            project__brand=self,
            project__is_published=True,
        ).order_by('-uploaded_at').first()


class CaseStudy(models.Model):
    """A portfolio piece tied to a brand."""
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='case_studies')
    title = models.CharField(max_length=200)
    project_year = models.PositiveIntegerField(
        default=timezone.now().year,
        verbose_name="Loyiha yili",
        help_text="Loyiha tashkil topgan yili"
    )
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    tags = models.CharField(
        max_length=300,
        blank=True,
        help_text="Vergul bilan: montaj, rang korektsiyasi, animatsiya"
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Ish namunasi"
        verbose_name_plural = "Ish namunalari"

    def __str__(self):
        return f"{self.brand.name} — {self.title}"

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def first_video(self):
        return self.videos.first()

    @property
    def first_image(self):
        return self.images.first()

    def get_primary_media(self):
        image = self.images.first()
        video = self.videos.first()
        if image:
            return image
        return video


class ProjectImage(models.Model):
    project = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/images/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Loyiha rasmlari'
        verbose_name_plural = 'Loyiha rasmlari'

    def __str__(self):
        return f"{self.project.title} - Image #{self.pk}"


class ProjectVideo(models.Model):
    project = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='projects/videos/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Loyiha video'
        verbose_name_plural = 'Loyiha videolari'

    def __str__(self):
        return f"{self.project.title} - Video #{self.pk}"

class UserBlockInfo(models.Model):
    """Bloklangan foydalanuvchi haqida admin yozgan sabab."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='block_info')
    reason = models.TextField(blank=True, verbose_name="Bloklash sababi")
    blocked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — bloklangan"
