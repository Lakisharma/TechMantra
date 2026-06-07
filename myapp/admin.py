from django.contrib import admin
from .models import Services, Admission, ContactMessage, StudentProfile, Course, GalleryImage, WebsiteSettings

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'course', 'created_at')
    search_fields = ('name', 'email', 'phone', 'course')
    list_filter = ('course', 'created_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)

from django.utils.html import format_html

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'get_username', 'get_email', 'phone', 'course', 'rank', 'grade', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'course')
    list_filter = ('course', 'grade', 'created_at')
    readonly_fields = ('get_thumbnail_large',)
    fields = ('user', 'photo', 'get_thumbnail_large', 'phone', 'course', 'rank', 'grade')

    def get_thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(255,255,255,0.15);" />', obj.photo.url)
        return format_html('<span style="color:#94a3b8;"><i class="fa-solid fa-user-circle" style="font-size:1.5rem;vertical-align:middle;"></i></span>')
    get_thumbnail.short_description = 'Photo'

    def get_thumbnail_large(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px; object-fit: cover; border: 1px solid rgba(0,0,0,0.1);" />', obj.photo.url)
        return "No profile photo uploaded"
    get_thumbnail_large.short_description = 'Photo Preview'

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'fee', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at')
    search_fields = ('title', 'category')
    list_filter = ('category', 'uploaded_at')


@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone')


from .models import AdminProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'get_created_by', 'created_at')
    search_fields = ('user__username', 'created_by__username')
    list_filter = ('created_at',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else 'System / Initial Setup'
    get_created_by.short_description = 'Created By'




