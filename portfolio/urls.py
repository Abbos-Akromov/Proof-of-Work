from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # ─── Public Views ──────────────────────────────────────
    path('', views.home, name='home'),
    path('brands/', views.brands, name='brands'),
    path('brand/<int:pk>/', views.brand_detail, name='brand_detail'),
    path('work/<int:pk>/', views.case_study_detail, name='case_study_detail'),
    
    # ─── Authentication ────────────────────────────────────
    path('login/', views.custom_login, name='custom_login'),
    path('register/', views.custom_register, name='custom_register'),
    path('logout/', views.custom_logout, name='custom_logout'),
    
    # ─── Dashboard & Profile ──────────────────────────────
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # ─── Brand CRUD ────────────────────────────────────────
    path('brand/create/', views.brand_create, name='brand_create'),
    path('brand/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('brand/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    
    # ─── Case Study CRUD ───────────────────────────────────
    path('work/create/', views.casestudy_create, name='casestudy_create'),
    path('work/<int:pk>/edit/', views.casestudy_edit, name='casestudy_edit'),
    path('work/<int:pk>/delete/', views.casestudy_delete, name='casestudy_delete'),

    # ─── User Management ───────────────────────────────────
    path('user/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('user/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # ─── Backward Compatibility Aliases ───────────────────
    path('admin-panel/login/', views.custom_login),
    path('admin-panel/logout/', views.custom_logout),
    path('admin-panel/', views.admin_dashboard),
    path('admin-panel/brands/add/', views.brand_create),
    path('admin-panel/brands/<int:pk>/edit/', views.brand_edit),
    path('admin-panel/brands/<int:pk>/delete/', views.brand_delete),
    path('admin-panel/works/add/', views.casestudy_create),
    path('admin-panel/works/<int:pk>/edit/', views.casestudy_edit),
    path('admin-panel/works/<int:pk>/delete/', views.casestudy_delete),
    path('api/footer/update/', views.api_footer_update, name='api_footer_update'),
]
