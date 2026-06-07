from django.db import models

# Create your models here.

class Services(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message  = models.TextField()

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

from django.contrib.auth.models import User

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
    site_name = models.CharField(max_length=100, default="TechMantra")
    site_logo = models.ImageField(upload_to='site_logos/', blank=True, null=True)
    contact_email = models.CharField(max_length=100, default="info@techmantra.com")
    contact_phone = models.CharField(max_length=50, default="+91 98765 43210")
    contact_address = models.TextField(default="Academy Address, Delhi, India")

    def __str__(self):
        return self.site_name


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_admins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} (Created by: {self.created_by.username if self.created_by else 'System'})"


