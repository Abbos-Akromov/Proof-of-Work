from django.contrib import admin
from .models import Profile, Brand, CaseStudy


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagline', 'updated_at')


class CaseStudyInline(admin.TabularInline):
    model = CaseStudy
    extra = 1
    fields = ('title', 'is_published', 'order')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'work_label', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    list_filter = ('category', 'is_featured')
    inlines = [CaseStudyInline]


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'is_published', 'order', 'created_at')
    list_filter = ('is_published', 'brand')
    list_editable = ('is_published', 'order')
