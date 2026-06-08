"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('file/', views.index, name='file_index'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('faculty/', views.faculty, name='faculty'),
    path('admissions/', views.admissions, name='admissions'),
    path('gallery/', views.gallery, name='gallery'),
    path('results/', views.results, name='results'),
    path('contact/', views.contact, name='contact'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
    path('login/', views.login_view, name='login'),
    path('create-admin-xyz/', views.temp_create_admin, name='temp_create_admin'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/update-student/<int:profile_id>/', views.admin_update_student_view, name='admin_update_student'),
    path('admin-dashboard/students/add/', views.admin_add_student_view, name='admin_add_student'),
    path('admin-dashboard/settings/update/', views.admin_update_settings_view, name='admin_update_settings'),
    path('admin-dashboard/approve-admission/<int:admission_id>/', views.admin_approve_admission_view, name='admin_approve_admission'),
    path('admin-dashboard/delete/<str:record_type>/<int:record_id>/', views.admin_delete_record_view, name='admin_delete_record'),
    path('admin-dashboard/courses/add/', views.admin_add_course_view, name='admin_add_course'),
    path('admin-dashboard/courses/delete/<int:course_id>/', views.admin_delete_course_view, name='admin_delete_course'),
    path('admin-dashboard/gallery/add/', views.admin_add_gallery_view, name='admin_add_gallery'),
    path('admin-dashboard/gallery/delete/<int:image_id>/', views.admin_delete_gallery_view, name='admin_delete_gallery'),
    path('admin-dashboard/admins/add/', views.admin_add_admin_view, name='admin_add_admin'),
    path('admin-dashboard/admins/delete/<int:admin_id>/', views.admin_delete_admin_view, name='admin_delete_admin'),
    path('admin-dashboard/admins/change-password/<int:admin_id>/', views.admin_change_admin_password_view, name='admin_change_admin_password'),
    path('admin-dashboard/certificates/add/', views.admin_add_certificate_view, name='admin_add_certificate'),
    path('admin-dashboard/certificates/delete/<int:cert_id>/', views.admin_delete_certificate_view, name='admin_delete_certificate'),
    path('admin-dashboard/certificates/edit/<int:cert_id>/', views.admin_edit_certificate_view, name='admin_edit_certificate'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


