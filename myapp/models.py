from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Services(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name

class Admission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    course = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.course}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20)
    course = models.CharField(max_length=100)
    rank = models.CharField(max_length=50, blank=True, null=True, default="N/A")
    grade = models.CharField(max_length=20, default="N/A")
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Course(models.Model):
    title = models.CharField(max_length=150)
    duration = models.CharField(max_length=50)
    fee = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    CATEGORY_CHOICES = (
        ('classrooms', 'Classrooms'),
        ('events', 'Events'),
        ('results', 'Results'),
        ('other', 'Activities'),
    )
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='gallery_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category})"


class WebsiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="TeachMANTRA")
    site_logo = models.ImageField(upload_to='site_logos/', blank=True, null=True)
    contact_email = models.CharField(max_length=100, default="info@teachmantra.com")
    contact_phone = models.CharField(max_length=50, default="+91 98765 43210")
    contact_address = models.TextField(default="Academy Address, Delhi, India")

    # Auto Entrance Popup Announcement Banner (Inspired by thedigicoders.com)
    show_popup = models.BooleanField(default=True, help_text="Show automatic announcement popup on website load")
    popup_title = models.CharField(max_length=150, default="ADMISSION OPEN 2026-27")
    popup_subtitle = models.TextField(default="Join the league of successful students at TeachMANTRA Academy. Job-oriented classroom coaching, structured mock tests & expert guidance. Register today to secure your seat!")
    popup_image = models.ImageField(upload_to='popup_banners/', blank=True, null=True)
    popup_phone = models.CharField(max_length=100, default="+91 98765 43210, +91 91234 56789")
    popup_btn1_text = models.CharField(max_length=50, default="Register Now")
    popup_btn1_link = models.CharField(max_length=150, default="/register/")
    popup_btn2_text = models.CharField(max_length=50, default="Explore Courses")
    popup_btn2_link = models.CharField(max_length=150, default="/courses/")

    def __str__(self):
        return self.site_name


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_admins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} (Created by: {self.created_by.username if self.created_by else 'System'})"


class Certificate(models.Model):
    certificate_id = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=150)
    course_name = models.CharField(max_length=150)
    rank = models.CharField(max_length=50, blank=True, null=True, default="N/A")
    duration = models.CharField(max_length=50)
    issue_date = models.CharField(max_length=100)
    grade = models.CharField(max_length=20, default="N/A")
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_id} - {self.student_name}"


class BroadcastEmail(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    audience_filter = models.CharField(max_length=100, default='all')
    recipient_count = models.IntegerField(default=0)
    recipients_list = models.TextField(blank=True, help_text="Comma-separated or listed recipient emails")
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_broadcasts')
    status = models.CharField(max_length=50, default='Delivered')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.subject} ({self.recipient_count} recipients)"
