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


class TeamMember(models.Model):
    MEMBER_TYPE_CHOICES = (
        ('founder', 'Co-Founder / Visionary'),
        ('team', 'Team Member / Faculty'),
    )
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text="e.g. CO-FOUNDER, TEAM LEAD (FULL STACK)")
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPE_CHOICES, default='team')
    tag_color = models.CharField(max_length=20, default='orange', help_text="orange or blue")
    image = models.ImageField(upload_to='team_images/', blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers come first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} - {self.role} ({self.get_member_type_display()})"



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


class OnlineTest(models.Model):
    title = models.CharField(max_length=200, default="GS MIX — Online Quiz")
    category = models.CharField(max_length=100, default="Mixed General Studies")
    subtitle = models.CharField(max_length=250, default="परीक्षा अभ्यास • Comprehensive Mock Test Series")
    description = models.TextField(blank=True, default="Practice general knowledge, current affairs, and mock test questions designed by TeachMANTRA expert faculty.")
    duration_minutes = models.IntegerField(default=30, help_text="Test time in minutes")
    total_questions = models.IntegerField(default=50, help_text="Target question count")
    pass_percentage = models.IntegerField(default=40, help_text="Passing percentage (e.g. 40)")
    external_link = models.CharField(max_length=500, blank=True, null=True, help_text="Optional external test portal or Google Form URL. Leave blank for interactive built-in portal.")
    is_active = models.BooleanField(default=True, help_text="Show in Home Page and Tests portal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"

    @property
    def questions_count(self):
        count = self.questions.count()
        return count if count > 0 else self.total_questions


class QuizQuestion(models.Model):
    OPTION_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )
    test = models.ForeignKey(OnlineTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(help_text="Question statement (Supports Hindi and English)")
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=5, choices=OPTION_CHOICES, default='A')
    explanation = models.TextField(blank=True, null=True, help_text="Explanation shown after test completion")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"[{self.test.title}] Q: {self.question_text[:50]}..."


class TestSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_submissions')
    test = models.ForeignKey(OnlineTest, on_delete=models.CASCADE, related_name='submissions')
    student_name = models.CharField(max_length=150)
    student_email = models.EmailField(blank=True, null=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    answers_json = models.TextField(blank=True, null=True, help_text="Recorded answers for review")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student_name} - {self.test.title} ({self.score}/{self.total_questions})"


class TopperResult(models.Model):
    name = models.CharField(max_length=150)
    exam_name = models.CharField(max_length=150, help_text="e.g. UP POLICE 2024, RRB NTPC 2024, NDA 2024")
    rank = models.CharField(max_length=100, help_text="e.g. AIR 16753, AIR 29, 98.6%")
    badge = models.CharField(max_length=100, default="Rank 1", help_text="e.g. Rank 1, Topper, Selected")
    image = models.ImageField(upload_to='toppers/', blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} - {self.exam_name} ({self.rank})"


