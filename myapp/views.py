import json
from django.db import models
from django.db.models import Q, Avg, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import (
    Services, Admission, ContactMessage, StudentProfile, Course, 
    GalleryImage, TeamMember, WebsiteSettings, AdminProfile, Certificate, 
    BroadcastEmail, OnlineTest, QuizQuestion, TestSubmission
)
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt

def index(request):
    populate_default_online_tests()
    success_msg = None
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        
        if name and email and message:
            Services.objects.create(name=name, email=email, message=message)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": "Data submitted successfully!"})
            success_msg = "Data submitted successfully!"
            
    active_tests = OnlineTest.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'index.html', {
        "success_msg": success_msg,
        "active_tests": active_tests
    })

def about(request):
    return render(request, 'about.html')

def courses(request):
    courses_list = Course.objects.all().order_by('-created_at')
    return render(request, 'courses.html', {"courses": courses_list})

def faculty(request):
    founders = TeamMember.objects.filter(member_type='founder').order_by('order', 'id')
    team_members = TeamMember.objects.filter(member_type='team').order_by('order', 'id')
    return render(request, 'faculty.html', {
        "founders": founders,
        "team_members": team_members
    })

def admissions(request):
    success_msg = None
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        course = request.POST.get("course")
        message = request.POST.get("message", "")
        
        if name and email and phone and course:
            Admission.objects.create(
                name=name,
                email=email,
                phone=phone,
                course=course,
                message=message
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": "Admission request submitted successfully!"})
            success_msg = "Admission request submitted successfully!"
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": "Please fill all required fields."})
            success_msg = "Error: Please fill all required fields."
            
    return render(request, 'admissions.html', {"success_msg": success_msg})

def gallery(request):
    images_list = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'gallery.html', {"images": images_list})

def results(request):
    return render(request, 'results.html')

def contact(request):
    success_msg = None
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        
        if name and email and phone and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": "Message sent successfully!"})
            success_msg = "Message sent successfully!"
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": "Please fill all required fields."})
            success_msg = "Error: Please fill all required fields."
            
    return render(request, 'contact.html', {"success_msg": success_msg})

def populate_default_certificates():
    defaults = [
        {
            "certificate_id": "TM-2026-101",
            "student_name": "Ankit Kumar",
            "course_name": "SSC CGL Coaching Program",
            "rank": "AIR 45",
            "duration": "6 Months",
            "issue_date": "May 15, 2026",
            "grade": "A+"
        },
        {
            "certificate_id": "TM-2026-102",
            "student_name": "Priya Sharma",
            "course_name": "Bank PO Prep Course",
            "rank": "AIR 78",
            "duration": "6 Months",
            "issue_date": "May 18, 2026",
            "grade": "A+"
        },
        {
            "certificate_id": "TM-2026-103",
            "student_name": "Rahul Verma",
            "course_name": "RRB NTPC Coaching",
            "rank": "AIR 29",
            "duration": "6 Months",
            "issue_date": "May 20, 2026",
            "grade": "A+"
        },
        {
            "certificate_id": "TM-2026-104",
            "student_name": "Neha Singh",
            "course_name": "NDA / CDS Exam Prep",
            "rank": "AIR 15",
            "duration": "1 Year",
            "issue_date": "May 22, 2026",
            "grade": "A++"
        }
    ]
    for d in defaults:
        Certificate.objects.get_or_create(
            certificate_id=d["certificate_id"],
            defaults=d
        )

def populate_default_online_tests():
    if not OnlineTest.objects.exists():
        test = OnlineTest.objects.create(
            title="GS MIX — Online Quiz",
            category="Mixed General Studies",
            subtitle="50 Questions • Mixed General Studies • परीक्षा अभ्यास",
            description="TeachMANTRA Academy All India Level Practice Mock Test Series for SSC CGL, Railway NTPC, Banking, State PCS & Competitive Exams.",
            duration_minutes=30,
            total_questions=10,
            pass_percentage=40,
            is_active=True
        )
        sample_questions = [
            {
                "question_text": "भारत में हरित क्रांति के जनक के रूप में किसे जाना जाता है?",
                "option_a": "एम. एस. स्वामीनाथन",
                "option_b": "नॉर्मन बोरलॉग",
                "option_c": "वर्गीज कुरियन",
                "option_d": "होमी भाभा",
                "correct_option": "A",
                "explanation": "डॉ. एम. एस. स्वामीनाथन को भारत में हरित क्रांति (Green Revolution) का जनक माना जाता है।",
                "order": 1
            },
            {
                "question_text": "भारतीय संविधान के किस अनुच्छेद के तहत वित्तीय आपातकाल की घोषणा की जाती है?",
                "option_a": "अनुच्छेद 352",
                "option_b": "अनुच्छेद 356",
                "option_c": "अनुच्छेद 360",
                "option_d": "अनुच्छेद 368",
                "correct_option": "C",
                "explanation": "अनुच्छेद 360 के तहत भारत के राष्ट्रपति को वित्तीय आपातकाल लगाने का अधिकार है।",
                "order": 2
            },
            {
                "question_text": "विश्व का सबसे बड़ा डेल्टा कौन सा है?",
                "option_a": "सुंदरवन डेल्टा",
                "option_b": "अमेज़ॅन डेल्टा",
                "option_c": "नील नदी डेल्टा",
                "option_d": "मिसिसिपी डेल्टा",
                "correct_option": "A",
                "explanation": "गंगा और ब्रह्मपुत्र नदियों द्वारा निर्मित सुंदरवन डेल्टा विश्व का सबसे बड़ा डेल्टा है।",
                "order": 3
            },
            {
                "question_text": "मानव शरीर में रक्त का शुद्धिकरण किस अंग में होता है?",
                "option_a": "हृदय (Heart)",
                "option_b": "वृक्क / गुर्दा (Kidney)",
                "option_c": "फेफड़े (Lungs)",
                "option_d": "यकृत (Liver)",
                "correct_option": "B",
                "explanation": "किडनी (Kidney) रक्त को छानकर अपशिष्ट पदार्थों को अलग करती है।",
                "order": 4
            },
            {
                "question_text": "Who is known as the 'Father of the Indian Constitution'?",
                "option_a": "Mahatma Gandhi",
                "option_b": "Dr. B. R. Ambedkar",
                "option_c": "Jawaharlal Nehru",
                "option_d": "Dr. Rajendra Prasad",
                "correct_option": "B",
                "explanation": "Dr. B. R. Ambedkar was the Chairman of the Drafting Committee of the Constitution of India.",
                "order": 5
            },
            {
                "question_text": "प्रकाश वर्ष (Light Year) किसकी इकाई है?",
                "option_a": "समय (Time)",
                "option_b": "दूरी (Distance)",
                "option_c": "प्रकाश की तीव्रता (Intensity of Light)",
                "option_d": "द्रव्यमान (Mass)",
                "correct_option": "B",
                "explanation": "प्रकाश वर्ष खगोलीय दूरी (Astronomical Distance) मापने की इकाई है।",
                "order": 6
            },
            {
                "question_text": "कर्क रेखा भारत के कितने राज्यों से होकर गुजरती है?",
                "option_a": "6 राज्य",
                "option_b": "7 राज्य",
                "option_c": "8 राज्य",
                "option_d": "9 राज्य",
                "correct_option": "C",
                "explanation": "कर्क रेखा भारत के 8 राज्यों (गुजरात, राजस्थान, मध्य प्रदेश, छत्तीसगढ़, झारखंड, पश्चिम बंगाल, त्रिपुरा, मिजोरम) से गुजरती है।",
                "order": 7
            },
            {
                "question_text": "Which gas is used in the manufacturing of Vanaspati Ghee from vegetable oil?",
                "option_a": "Oxygen",
                "option_b": "Nitrogen",
                "option_c": "Hydrogen",
                "option_d": "Carbon Dioxide",
                "correct_option": "C",
                "explanation": "Hydrogenation process using Nickel catalyst and Hydrogen gas converts vegetable oil to ghee.",
                "order": 8
            },
            {
                "question_text": "भारतीय रिजर्व बैंक (RBI) की स्थापना किस वर्ष हुई थी?",
                "option_a": "1935",
                "option_b": "1947",
                "option_c": "1950",
                "option_d": "1969",
                "correct_option": "A",
                "explanation": "भारतीय रिजर्व बैंक की स्थापना 1 अप्रैल 1935 को RBI अधिनियम 1934 के तहत की गई थी।",
                "order": 9
            },
            {
                "question_text": "पानीपत का प्रथम युद्ध (First Battle of Panipat) किस वर्ष लड़ा गया था?",
                "option_a": "1526",
                "option_b": "1556",
                "option_c": "1761",
                "option_d": "1576",
                "correct_option": "A",
                "explanation": "21 अप्रैल 1526 को बाबर और इब्राहिम लोदी के बीच पानीपत की पहली लड़ाई लड़ी गई थी।",
                "order": 10
            }
        ]
        for q in sample_questions:
            QuizQuestion.objects.create(test=test, **q)


def verify_certificate(request):
    if request.GET.get('debug_storage') == '1':
        import os
        from django.core.files.storage import default_storage
        keys = [k for k in os.environ.keys() if 'CLOUDINARY' in k.upper() or 'POSTGRES' in k.upper()]
        return JsonResponse({
            "storage_backend": default_storage.__class__.__name__,
            "found_env_keys": keys,
            "has_cloudinary_url": bool(os.environ.get('CLOUDINARY_URL')),
            "has_cloudinary_cloud_name": bool(os.environ.get('CLOUDINARY_CLOUD_NAME')),
        })

    populate_default_certificates()
    
    cert_id = request.GET.get("cert_id") or request.POST.get("cert_id")
    searched = False
    found = False
    details = None
    
    if cert_id:
        searched = True
        cert_id = cert_id.strip().upper()
        try:
            cert = Certificate.objects.get(certificate_id=cert_id)
            found = True
            details = {
                "id": cert.certificate_id,
                "name": cert.student_name,
                "course": cert.course_name,
                "rank": cert.rank,
                "duration": cert.duration,
                "issue_date": cert.issue_date,
                "grade": cert.grade,
                "file_url": cert.certificate_file.url if cert.certificate_file else None
            }
        except Certificate.DoesNotExist:
            found = False
            
    return render(request, 'verify_certificate.html', {
        "searched": searched,
        "found": found,
        "details": details,
        "cert_id": cert_id
    })


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import StudentProfile
from django.shortcuts import redirect

def register_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/profile/'
    if request.user.is_authenticated:
        return redirect(next_url)
        
    courses_list = [
        "SSC CGL Coaching Program",
        "Bank PO Prep Course",
        "RRB NTPC Coaching",
        "NDA / CDS Exam Prep"
    ]
    
    if request.method == "POST":
        next_url = request.POST.get('next') or request.GET.get('next') or '/profile/'
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        course = request.POST.get("course")
        full_name = request.POST.get("full_name", "")
        
        # Validation
        if not username or not email or not password or not phone or not course:
            msg = "Please fill all required fields."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list, "next": next_url})
            
        if User.objects.filter(username=username).exists():
            msg = "Username already exists."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list, "next": next_url})
            
        if User.objects.filter(email=email).exists():
            msg = "Email already registered."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list, "next": next_url})
            
        # Create User
        first_name = full_name
        last_name = ""
        if " " in full_name:
            parts = full_name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1]
            
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create StudentProfile
        # Set a default rank and grade for new users
        StudentProfile.objects.create(
            user=user,
            phone=phone,
            course=course,
            rank="N/A",
            grade="N/A"
        )
        
        login(request, user)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({"status": "success", "message": "Registration successful!", "redirect_url": next_url})
        return redirect(next_url)
        
    return render(request, 'register.html', {"courses": courses_list, "next": next_url})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/profile/'
    if request.user.is_authenticated:
        return redirect(next_url)
        
    if request.method == "POST":
        next_url = request.POST.get('next') or request.GET.get('next') or '/profile/'
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if not username or not password:
            msg = "Please provide both username and password."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'login.html', {"error_msg": msg, "next": next_url})
            
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": "Login successful!", "redirect_url": next_url})
            return redirect(next_url)
        else:
            msg = "Invalid username or password."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'login.html', {"error_msg": msg, "next": next_url})
            
    return render(request, 'login.html', {"next": next_url})


from django.http import HttpResponse

def temp_create_admin(request):
    try:
        from django.db import connection
        engine = connection.settings_dict.get('ENGINE')
        db_name = connection.settings_dict.get('NAME')
        username = 'admin'
        password = 'Adminpassword123!'
        email = 'admin@techmantra.com'
        
        # Explicitly run migrate to ensure database tables are created
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            return HttpResponse(f"SUCCESS: Admin user '{username}' password updated successfully to '{password}' on database engine: {engine} ({db_name})")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            return HttpResponse(f"SUCCESS: Admin user '{username}' created successfully with password: '{password}' on database engine: {engine} ({db_name})")
    except Exception as e:
        from django.db import connection
        engine = connection.settings_dict.get('ENGINE')
        return HttpResponse(f"Error on engine {engine}: {e}")




@login_required(login_url='login')
def profile_view(request):
    populate_default_online_tests()
    
    # Ensure profile exists for the user (handles superusers/staff created via CLI)
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": "N/A",
            "course": "N/A",
            "rank": "N/A",
            "grade": "N/A"
        }
    )
    
    if request.method == "POST":
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
            profile.save()
            msg = "Profile photo updated successfully!"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": msg, "redirect_url": "/profile/"})
            return redirect('profile')
            
    user_fullname = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    matching_cert = None
    
    # Query database dynamically
    db_certs = Certificate.objects.filter(student_name__iexact=user_fullname)
    if not db_certs.exists():
        db_certs = Certificate.objects.filter(student_name__icontains=request.user.username)
        
    db_cert = db_certs.first()
    if db_cert:
        matching_cert = {
            "id": db_cert.certificate_id,
            "name": db_cert.student_name,
            "course": db_cert.course_name,
            "rank": db_cert.rank,
            "grade": db_cert.grade,
            "file_url": db_cert.certificate_file.url if db_cert.certificate_file else None
        }

    # Available Tests for the student
    available_tests = OnlineTest.objects.filter(is_active=True).order_by('-created_at')

    # Student Test Submissions & Performance History
    my_submissions = TestSubmission.objects.filter(
        models.Q(user=request.user) | 
        models.Q(student_email=request.user.email) | 
        models.Q(student_name__iexact=user_fullname) |
        models.Q(student_name__icontains=request.user.username)
    ).order_by('-submitted_at')

    total_tests_attempted = my_submissions.count()
    tests_passed = my_submissions.filter(passed=True).count()
    tests_failed = total_tests_attempted - tests_passed
    
    # Calculate average score percentage
    avg_score_raw = my_submissions.aggregate(models.Avg('percentage'))['percentage__avg']
    avg_score = round(avg_score_raw, 1) if avg_score_raw is not None else 0
            
    return render(request, 'profile.html', {
        "profile": profile,
        "matching_cert": matching_cert,
        "available_tests": available_tests,
        "my_submissions": my_submissions,
        "total_tests_attempted": total_tests_attempted,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "avg_score": avg_score
    })


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == "POST":
        identity = request.POST.get("identity")
        
        if not identity:
            msg = "Please enter your username or email."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'forgot_password.html', {"error_msg": msg})
            
        user = User.objects.filter(username=identity).first() or User.objects.filter(email=identity).first()
        if user:
            user.set_password("TM-Reset123")
            user.save()
            msg = "Password reset successfully! (Demo password: TM-Reset123)"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": msg, "redirect_url": "/login/"})
            return render(request, 'forgot_password.html', {"success_msg": msg})
        else:
            msg = "No account found with that username or email."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'forgot_password.html', {"error_msg": msg})
            
    return render(request, 'forgot_password.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def admin_dashboard_view(request):
    if not request.user.is_staff:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({"status": "error", "message": "Access denied. Admin permissions required."})
        return redirect('home')

    populate_default_certificates()
    populate_default_online_tests()

    students = StudentProfile.objects.select_related('user').all()
    admissions = Admission.objects.all().order_by('-created_at')
    contacts = ContactMessage.objects.all().order_by('-created_at')
    courses_list = Course.objects.all().order_by('-created_at')
    images_list = GalleryImage.objects.all().order_by('-uploaded_at')
    founders_list = TeamMember.objects.filter(member_type='founder').order_by('order', 'id')
    team_list = TeamMember.objects.filter(member_type='team').order_by('order', 'id')
    certificates_list = Certificate.objects.all().order_by('-created_at')
    broadcast_emails = BroadcastEmail.objects.all().order_by('-created_at')
    online_tests = OnlineTest.objects.all().prefetch_related('questions', 'submissions').order_by('-created_at')
    test_submissions = TestSubmission.objects.all().select_related('test').order_by('-submitted_at')[:50]

    # Fetch and ensure profiles for admins
    admins = User.objects.filter(is_staff=True).order_by('date_joined')
    for admin in admins:
        AdminProfile.objects.get_or_create(user=admin)

    # Debug environment variables & storage backend
    import os
    from django.core.files.storage import default_storage
    cloudinary_keys = [k for k in os.environ.keys() if 'CLOUDINARY' in k.upper()]
    storage_class = default_storage.__class__.__name__
    debug_info = {
        "cloudinary_keys": cloudinary_keys,
        "storage_class": storage_class,
    }

    # Count stats
    total_students = students.exclude(user__is_staff=True).count()
    pending_admissions = admissions.count()
    contact_messages = contacts.count()
    total_courses = courses_list.count()
    total_images = images_list.count()
    total_team = TeamMember.objects.count()
    total_admins = admins.count()
    total_certificates = certificates_list.count()
    total_broadcasts = broadcast_emails.count()
    total_online_tests = online_tests.count()

    return render(request, 'admin_dashboard.html', {
        "students": students,
        "admissions": admissions,
        "contacts": contacts,
        "courses": courses_list,
        "gallery_images": images_list,
        "founders": founders_list,
        "team_members": team_list,
        "admins": admins,
        "certificates": certificates_list,
        "broadcast_emails": broadcast_emails,
        "online_tests": online_tests,
        "test_submissions": test_submissions,
        "debug_info": debug_info,
        "stats": {
            "total_students": total_students,
            "pending_admissions": pending_admissions,
            "contact_messages": contact_messages,
            "total_courses": total_courses,
            "total_images": total_images,
            "total_team": total_team,
            "total_admins": total_admins,
            "total_certificates": total_certificates,
            "total_broadcasts": total_broadcasts,
            "total_online_tests": total_online_tests
        }
    })



@login_required(login_url='login')
def admin_update_student_view(request, profile_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name", "")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        course = request.POST.get("course")
        rank = request.POST.get("rank", "N/A")
        grade = request.POST.get("grade", "N/A")
        password = request.POST.get("password")
        status = request.POST.get("status")
        
        if not username or not email or not phone or not course:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        try:
            profile = StudentProfile.objects.select_related('user').get(id=profile_id)
            user = profile.user
            
            # Check username uniqueness if it changed
            if username != user.username and User.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username already exists."})
                
            # Check email uniqueness if it changed
            if email != user.email and User.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email already registered."})

            # Update User
            user.username = username
            user.email = email
            
            if status in ['active', 'inactive']:
                user.is_active = (status == 'active')
                
            if password:
                user.set_password(password)
            
            first_name = full_name
            last_name = ""
            if " " in full_name:
                parts = full_name.split(" ", 1)
                first_name = parts[0]
                last_name = parts[1]
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Update Profile
            profile.phone = phone
            profile.course = course
            profile.rank = rank
            profile.grade = grade
            if 'photo' in request.FILES:
                profile.photo = request.FILES['photo']
            profile.save()
            return JsonResponse({"status": "success", "message": "Student profile updated successfully!"})
        except StudentProfile.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student profile not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_add_student_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name", "")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        course = request.POST.get("course")
        password = request.POST.get("password")
        rank = request.POST.get("rank", "N/A") or "N/A"
        grade = request.POST.get("grade", "N/A") or "N/A"
        photo = request.FILES.get("photo")

        # Required fields validation
        if not username or not email or not phone or not course or not password:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        # Uniqueness validation
        if User.objects.filter(username=username).exists():
            return JsonResponse({"status": "error", "message": "Username already exists."})
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already registered."})

        try:
            # Create User
            first_name = full_name
            last_name = ""
            if " " in full_name:
                parts = full_name.split(" ", 1)
                first_name = parts[0]
                last_name = parts[1]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Create StudentProfile
            StudentProfile.objects.create(
                user=user,
                phone=phone,
                course=course,
                rank=rank,
                grade=grade,
                photo=photo
            )
            return JsonResponse({"status": "success", "message": "Student account created successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_update_settings_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        site_name = request.POST.get("site_name")
        contact_email = request.POST.get("contact_email")
        contact_phone = request.POST.get("contact_phone")
        contact_address = request.POST.get("contact_address")
        site_logo = request.FILES.get("site_logo")

        if not site_name or not contact_email or not contact_phone or not contact_address:
            return JsonResponse({"status": "error", "message": "Please fill all required settings fields."})

        try:
            settings, created = WebsiteSettings.objects.get_or_create(id=1)
            settings.site_name = site_name
            settings.contact_email = contact_email
            settings.contact_phone = contact_phone
            settings.contact_address = contact_address
            if site_logo:
                settings.site_logo = site_logo

            # Popup Announcement Settings
            show_popup_val = request.POST.get("show_popup")
            settings.show_popup = (show_popup_val in ['true', 'on', '1', True])
            settings.popup_title = request.POST.get("popup_title", settings.popup_title)
            settings.popup_subtitle = request.POST.get("popup_subtitle", settings.popup_subtitle)
            settings.popup_phone = request.POST.get("popup_phone", settings.popup_phone)
            settings.popup_btn1_text = request.POST.get("popup_btn1_text", settings.popup_btn1_text)
            settings.popup_btn1_link = request.POST.get("popup_btn1_link", settings.popup_btn1_link)
            settings.popup_btn2_text = request.POST.get("popup_btn2_text", settings.popup_btn2_text)
            settings.popup_btn2_link = request.POST.get("popup_btn2_link", settings.popup_btn2_link)
            if 'popup_image' in request.FILES:
                settings.popup_image = request.FILES['popup_image']

            settings.save()
            return JsonResponse({"status": "success", "message": "Website settings and popup banner updated successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_approve_admission_view(request, admission_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            admission = Admission.objects.get(id=admission_id)
            
            # Generate a clean unique username
            base_username = admission.name.lower().strip().replace(" ", "_")
            base_username = "".join(c for c in base_username if c.isalnum() or c == "_")
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            # Create User
            first_name = admission.name
            last_name = ""
            if " " in admission.name:
                parts = admission.name.split(" ", 1)
                first_name = parts[0]
                last_name = parts[1]
                
            user = User.objects.create_user(
                username=username,
                email=admission.email,
                password="TM-Welcome2026",
                first_name=first_name,
                last_name=last_name
            )
            
            # Create StudentProfile
            StudentProfile.objects.create(
                user=user,
                phone=admission.phone,
                course=admission.course,
                rank="N/A",
                grade="N/A"
            )
            
            # Delete Admission record
            admission.delete()
            
            return JsonResponse({
                "status": "success", 
                "message": f"Admission approved! Account '{username}' created with temporary password 'TM-Welcome2026'."
            })
            
        except Admission.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Admission enquiry not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_delete_record_view(request, record_type, record_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            if record_type == "student":
                profile = StudentProfile.objects.get(id=record_id)
                user = profile.user
                profile.delete()
                user.delete()
            elif record_type == "admission":
                Admission.objects.get(id=record_id).delete()
            elif record_type == "contact":
                ContactMessage.objects.get(id=record_id).delete()
            else:
                return JsonResponse({"status": "error", "message": "Invalid record type."})
                
            return JsonResponse({"status": "success", "message": "Record deleted successfully!"})
            
        except (StudentProfile.DoesNotExist, Admission.DoesNotExist, ContactMessage.DoesNotExist):
            return JsonResponse({"status": "error", "message": "Record not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_add_course_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        title = request.POST.get("title")
        duration = request.POST.get("duration")
        fee = request.POST.get("fee")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        if not title or not duration or not fee or not description:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        try:
            fee_val = int(fee)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Fee must be a valid number."})

        try:
            Course.objects.create(
                title=title,
                duration=duration,
                fee=fee_val,
                description=description,
                image=image
            )
            return JsonResponse({"status": "success", "message": "Course added successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_delete_course_view(request, course_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            course = Course.objects.get(id=course_id)
            course.delete()
            return JsonResponse({"status": "success", "message": "Course deleted successfully!"})
        except Course.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Course not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_add_gallery_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip()
        image = request.FILES.get("image")

        if not title or not category or not image:
            return JsonResponse({"status": "error", "message": "Please fill all fields and select an image."})

        try:
            img = GalleryImage.objects.create(
                title=title,
                category=category,
                image=image
            )
            return JsonResponse({
                "status": "success", 
                "message": "Gallery image uploaded successfully!",
                "image_id": img.id
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_update_gallery_view(request, image_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    try:
        img = GalleryImage.objects.get(id=image_id)
    except GalleryImage.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Gallery image not found."})

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip()

        if not title or not category:
            return JsonResponse({"status": "error", "message": "Title and album category are required."})

        img.title = title
        img.category = category

        if 'image' in request.FILES and request.FILES['image']:
            img.image = request.FILES['image']

        img.save()

        return JsonResponse({
            "status": "success",
            "message": "Gallery photo updated successfully!",
            "image_id": img.id,
            "title": img.title,
            "category": img.get_category_display() if hasattr(img, 'get_category_display') else img.category,
            "image_url": img.image.url if img.image else None
        })

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_delete_gallery_view(request, image_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            img = GalleryImage.objects.get(id=image_id)
            img.delete()
            return JsonResponse({"status": "success", "message": "Gallery image deleted successfully!"})
        except GalleryImage.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Gallery image not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


# ==========================================
# FACULTY & TEAM MANAGEMENT VIEWS
# ==========================================
@csrf_exempt
@login_required(login_url='login')
def admin_add_team_member_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        role = request.POST.get("role", "").strip()
        member_type = request.POST.get("member_type", "team").strip()
        tag_color = request.POST.get("tag_color", "blue").strip()
        order = request.POST.get("order", "0").strip()
        image = request.FILES.get("image")

        if not name or not role:
            return JsonResponse({"status": "error", "message": "Name and Designation / Role are required."})

        try:
            order_val = int(order) if order.isdigit() else 0
        except ValueError:
            order_val = 0

        try:
            member = TeamMember.objects.create(
                name=name,
                role=role,
                member_type=member_type,
                tag_color=tag_color,
                order=order_val,
                image=image
            )
            return JsonResponse({
                "status": "success",
                "message": f"'{name}' added to {member.get_member_type_display()} successfully!",
                "member_id": member.id
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error adding member: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_update_team_member_view(request, member_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    try:
        member = TeamMember.objects.get(id=member_id)
    except TeamMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Member record not found."})

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        role = request.POST.get("role", "").strip()
        member_type = request.POST.get("member_type", "").strip()
        tag_color = request.POST.get("tag_color", "").strip()
        order = request.POST.get("order", "").strip()

        if not name or not role:
            return JsonResponse({"status": "error", "message": "Name and Designation / Role are required."})

        member.name = name
        member.role = role
        if member_type in ['founder', 'team']:
            member.member_type = member_type
        if tag_color:
            member.tag_color = tag_color
        if order != "":
            try:
                member.order = int(order)
            except ValueError:
                pass

        if 'image' in request.FILES and request.FILES['image']:
            member.image = request.FILES['image']

        member.save()

        return JsonResponse({
            "status": "success",
            "message": f"Details for '{member.name}' updated successfully!",
            "member_id": member.id,
            "name": member.name,
            "role": member.role,
            "member_type": member.member_type,
            "image_url": member.image.url if member.image else None
        })

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_delete_team_member_view(request, member_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            member = TeamMember.objects.get(id=member_id)
            name = member.name
            member.delete()
            return JsonResponse({"status": "success", "message": f"'{name}' deleted successfully!"})
        except TeamMember.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Member not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_add_admin_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name", "")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        if User.objects.filter(username=username).exists():
            return JsonResponse({"status": "error", "message": "Username already exists."})

        if User.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already registered."})

        try:
            first_name = full_name
            last_name = ""
            if " " in full_name:
                parts = full_name.split(" ", 1)
                first_name = parts[0]
                last_name = parts[1]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True
            )

            # Create AdminProfile tracking creator
            AdminProfile.objects.create(
                user=user,
                created_by=request.user
            )

            return JsonResponse({"status": "success", "message": "Admin account created successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_delete_admin_view(request, admin_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        if request.user.id == admin_id:
            return JsonResponse({"status": "error", "message": "You cannot delete your own account."})

        try:
            user = User.objects.get(id=admin_id, is_staff=True)
            user.delete()
            return JsonResponse({"status": "success", "message": "Admin account deleted successfully!"})
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Admin user not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_change_admin_password_view(request, admin_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied. Admin permissions required."})

    if request.method == "POST":
        password = request.POST.get("password")
        if not password:
            return JsonResponse({"status": "error", "message": "Password cannot be empty."})

        try:
            # Ensure we are changing password of an admin/staff user
            target_admin = User.objects.get(id=admin_id, is_staff=True)
            target_admin.set_password(password)
            target_admin.save()
            return JsonResponse({"status": "success", "message": f"Password for '{target_admin.username}' updated successfully!"})
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Admin user not found."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_add_certificate_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        certificate_id = request.POST.get("certificate_id")
        student_name = request.POST.get("student_name")
        course_name = request.POST.get("course_name")
        rank = request.POST.get("rank", "N/A") or "N/A"
        duration = request.POST.get("duration")
        issue_date = request.POST.get("issue_date")
        grade = request.POST.get("grade", "N/A") or "N/A"

        if not certificate_id or not student_name or not course_name or not duration or not issue_date:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        # Check uniqueness of certificate_id
        if Certificate.objects.filter(certificate_id=certificate_id).exists():
            return JsonResponse({"status": "error", "message": f"Certificate ID '{certificate_id}' already exists."})

        certificate_file = request.FILES.get("certificate_file")

        try:
            Certificate.objects.create(
                certificate_id=certificate_id,
                student_name=student_name,
                course_name=course_name,
                rank=rank,
                duration=duration,
                issue_date=issue_date,
                grade=grade,
                certificate_file=certificate_file
            )
            return JsonResponse({"status": "success", "message": "Certificate added successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_delete_certificate_view(request, cert_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            cert = Certificate.objects.get(id=cert_id)
            cert.delete()
            return JsonResponse({"status": "success", "message": "Certificate deleted successfully!"})
        except Certificate.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Certificate not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_edit_certificate_view(request, cert_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            cert = Certificate.objects.get(id=cert_id)
        except Certificate.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Certificate not found."})

        certificate_id = request.POST.get("certificate_id")
        student_name = request.POST.get("student_name")
        course_name = request.POST.get("course_name")
        rank = request.POST.get("rank", "N/A") or "N/A"
        duration = request.POST.get("duration")
        issue_date = request.POST.get("issue_date")
        grade = request.POST.get("grade", "N/A") or "N/A"

        if not certificate_id or not student_name or not course_name or not duration or not issue_date:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        # Check uniqueness of certificate_id (excluding self)
        if Certificate.objects.filter(certificate_id=certificate_id).exclude(id=cert_id).exists():
            return JsonResponse({"status": "error", "message": f"Certificate ID '{certificate_id}' already exists."})

        certificate_file = request.FILES.get("certificate_file")

        try:
            cert.certificate_id = certificate_id
            cert.student_name = student_name
            cert.course_name = course_name
            cert.rank = rank
            cert.duration = duration
            cert.issue_date = issue_date
            cert.grade = grade
            if certificate_file:
                cert.certificate_file = certificate_file
            cert.save()
            return JsonResponse({"status": "success", "message": "Certificate updated successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_send_broadcast_mail_view(request):
    """
    Sends an announcement/broadcast email to all students or students of a selected course.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied. Admin privileges required."})

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        message_body = request.POST.get("message", "").strip()
        audience = request.POST.get("audience", "all").strip()

        if not subject:
            return JsonResponse({"status": "error", "message": "Please provide an email subject."})
        if not message_body:
            return JsonResponse({"status": "error", "message": "Please provide the message body."})

        # Fetch target students
        students_qs = StudentProfile.objects.select_related('user').filter(
            user__is_active=True
        ).exclude(user__is_staff=True)

        if audience and audience != 'all':
            students_qs = students_qs.filter(course=audience)

        # Collect distinct student emails
        recipient_emails = []
        for profile in students_qs:
            if profile.user.email and profile.user.email.strip():
                clean_email = profile.user.email.strip()
                if clean_email not in recipient_emails:
                    recipient_emails.append(clean_email)

        if not recipient_emails:
            return JsonResponse({
                "status": "error",
                "message": f"No registered students with valid email addresses found for the audience '{audience}'."
            })

        # Get website configuration branding
        site_settings = WebsiteSettings.objects.first()
        site_name = site_settings.site_name if site_settings else "TeachMANTRA Academy"
        site_email = site_settings.contact_email if site_settings else "support@teachmantra.com"
        site_phone = site_settings.contact_phone if site_settings else "+91 98765 43210"
        site_address = site_settings.contact_address if site_settings else "Academy Campus, Delhi, India"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f"{site_name} <noreply@teachmantra.com>")

        # Create beautiful responsive HTML email
        formatted_message_html = message_body.replace("\n", "<br>")
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    background-color: #0b0a1a;
                    margin: 0;
                    padding: 30px 15px;
                    color: #1e293b;
                }}
                .email-wrapper {{
                    max-width: 620px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
                    border: 1px solid rgba(226, 232, 240, 0.8);
                }}
                .email-header {{
                    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #ec4899 100%);
                    padding: 35px 25px;
                    text-align: center;
                    color: #ffffff;
                }}
                .email-header h1 {{
                    margin: 0;
                    font-size: 26px;
                    font-weight: 800;
                    letter-spacing: -0.5px;
                }}
                .email-badge {{
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.25);
                    backdrop-filter: blur(4px);
                    color: #ffffff;
                    padding: 5px 14px;
                    border-radius: 50px;
                    font-size: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-top: 10px;
                }}
                .email-body {{
                    padding: 32px 28px;
                    line-height: 1.7;
                    font-size: 15px;
                    color: #334155;
                }}
                .salutation {{
                    font-size: 16px;
                    font-weight: 700;
                    color: #0f172a;
                    margin-bottom: 12px;
                }}
                .notice-box {{
                    background: #f8fafc;
                    border-left: 4px solid #6366f1;
                    border-radius: 8px;
                    padding: 22px;
                    margin: 22px 0;
                    border-top: 1px solid #e2e8f0;
                    border-right: 1px solid #e2e8f0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .notice-title {{
                    font-size: 18px;
                    font-weight: 800;
                    color: #1e1b4b;
                    margin: 0 0 12px 0;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .notice-content {{
                    font-size: 15px;
                    color: #1e293b;
                    line-height: 1.75;
                }}
                .portal-cta {{
                    text-align: center;
                    margin: 30px 0 15px;
                }}
                .btn-cta {{
                    display: inline-block;
                    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
                    color: #ffffff !important;
                    font-weight: 700;
                    font-size: 14px;
                    padding: 12px 28px;
                    border-radius: 8px;
                    text-decoration: none;
                    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
                }}
                .email-footer {{
                    background: #f1f5f9;
                    padding: 22px;
                    text-align: center;
                    font-size: 12px;
                    color: #64748b;
                    border-top: 1px solid #e2e8f0;
                }}
                .email-footer p {{
                    margin: 4px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="email-header">
                    <h1>{site_name}</h1>
                    <div class="email-badge">📢 Official Notice</div>
                </div>
                <div class="email-body">
                    <div class="salutation">Dear Student,</div>
                    <p>We are writing to share an important official announcement from <strong>{site_name}</strong> administration:</p>
                    
                    <div class="notice-box">
                        <div class="notice-title">📌 {subject}</div>
                        <div class="notice-content">
                            {formatted_message_html}
                        </div>
                    </div>

                    <p style="font-size: 13px; color: #64748b; margin-top: 20px;">
                        Please take note of the above update. For any questions or queries, please feel free to reach out to the academy helpdesk.
                    </p>

                    <div class="portal-cta">
                        <a href="http://127.0.0.1:8000/profile/" class="btn-cta">Access Student Portal &rarr;</a>
                    </div>
                </div>
                <div class="email-footer">
                    <p><strong>{site_name}</strong></p>
                    <p>{site_address}</p>
                    <p>Contact: {site_phone} | {site_email}</p>
                    <p style="margin-top: 10px; color: #94a3b8; font-size: 11px;">
                        This email was automatically dispatched to all registered academy students.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_text = f"Dear Student,\n\n{subject}\n\n{message_body}\n\nRegards,\n{site_name}\n{site_address}\nPhone: {site_phone}"

        delivery_status = "Delivered"
        smtp_note = ""

        # Dispatch emails
        try:
            # Send using BCC so individual student addresses remain confidential
            mail = EmailMultiAlternatives(
                subject=f"[{site_name}] {subject}",
                body=plain_text,
                from_email=from_email,
                to=[from_email],
                bcc=recipient_emails
            )
            mail.attach_alternative(html_content, "text/html")
            mail.send(fail_silently=False)
        except Exception as e:
            # If SMTP host/credentials aren't active in dev, gracefully record that email was logged
            delivery_status = "Logged (SMTP Notice)"
            smtp_note = f" Note: SMTP Server returned '{str(e)}'. The announcement has been safely logged in your dashboard database."

        # Save record in BroadcastEmail history
        audience_display = "All Registered Students" if audience == 'all' else f"Course: {audience}"
        broadcast_record = BroadcastEmail.objects.create(
            subject=subject,
            message=message_body,
            audience_filter=audience_display,
            recipient_count=len(recipient_emails),
            recipients_list=", ".join(recipient_emails),
            sent_by=request.user,
            status=delivery_status
        )

        return JsonResponse({
            "status": "success",
            "message": f"Broadcast successfully dispatched to {len(recipient_emails)} students!{smtp_note}",
            "recipient_count": len(recipient_emails),
            "log_id": broadcast_record.id,
            "created_at": broadcast_record.created_at.strftime("%b %d, %Y %I:%M %p"),
            "status_label": delivery_status
        })

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_delete_broadcast_log_view(request, log_id):
    """
    Deletes a broadcast history record.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            log = BroadcastEmail.objects.get(id=log_id)
            log.delete()
            return JsonResponse({"status": "success", "message": "Broadcast log deleted successfully!"})
        except BroadcastEmail.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Broadcast log not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


# ==============================================================================
# ONLINE TESTS & QUIZ SYSTEM VIEWS (PUBLIC + ADMIN)
# ==============================================================================

def tests_list_view(request):
    """
    Public listing of all available mock tests and practice quizzes.
    """
    populate_default_online_tests()
    tests = OnlineTest.objects.filter(is_active=True).prefetch_related('questions').order_by('-created_at')
    return render(request, 'tests_list.html', {
        "tests": tests
    })


@login_required(login_url='login')
def take_test_view(request, test_id):
    """
    Interactive test/quiz page matching the modern exam interface.
    Requires student authentication to start.
    """
    populate_default_online_tests()
    test = get_object_or_404(OnlineTest, id=test_id)
    
    # If test has an external link and user opted for redirect
    if test.external_link and request.GET.get('launch_external') == '1':
        return redirect(test.external_link)

    questions = test.questions.all().order_by('order', 'id')
    
    # Serialize questions for client-side instant navigation
    questions_list = []
    for idx, q in enumerate(questions, start=1):
        questions_list.append({
            "id": q.id,
            "number": idx,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "order": q.order
        })

    return render(request, 'quiz.html', {
        "test": test,
        "questions_count": questions.count(),
        "questions_json": json.dumps(questions_list, ensure_ascii=False)
    })


@csrf_exempt
@login_required(login_url='login')
def submit_test_view(request, test_id):
    """
    Processes quiz answers submitted via AJAX, evaluates score, records submission,
    and returns detailed scorecard with explanations.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method."})

    test = get_object_or_404(OnlineTest, id=test_id)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    student_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    student_email = request.user.email or f"{request.user.username}@techmantra.com"
    user_answers = data.get("answers", {})  # e.g. {"1": "A", "2": "C"}

    questions = test.questions.all().order_by('order', 'id')
    total_q = questions.count()
    if total_q == 0:
        return JsonResponse({"status": "error", "message": "No questions available in this test."})

    score = 0
    review_list = []

    for idx, q in enumerate(questions, start=1):
        # Answers dict keys might be string or int
        ans = user_answers.get(str(q.id)) or user_answers.get(q.id) or None
        is_correct = (ans == q.correct_option)
        if is_correct:
            score += 1
            
        review_list.append({
            "number": idx,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "user_answer": ans,
            "correct_answer": q.correct_option,
            "is_correct": is_correct,
            "explanation": q.explanation or ""
        })

    percentage = round((score / total_q) * 100, 1)
    passed = percentage >= test.pass_percentage

    # Record submission in database with foreign key to User
    TestSubmission.objects.create(
        user=request.user,
        test=test,
        student_name=student_name,
        student_email=student_email,
        score=score,
        total_questions=total_q,
        percentage=percentage,
        passed=passed,
        answers_json=json.dumps(user_answers)
    )

    return JsonResponse({
        "status": "success",
        "student_name": student_name,
        "score": score,
        "total_questions": total_q,
        "percentage": percentage,
        "passed": passed,
        "pass_percentage": test.pass_percentage,
        "review": review_list
    })


@login_required(login_url='login')
def admin_add_test_view(request):
    """
    Creates a new Online Test from Admin Dashboard.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip() or "General Studies"
        subtitle = request.POST.get("subtitle", "").strip() or "परीक्षा अभ्यास • Mock Test Series"
        description = request.POST.get("description", "").strip()
        
        try:
            duration_minutes = int(request.POST.get("duration_minutes") or 30)
        except (ValueError, TypeError):
            duration_minutes = 30
            
        try:
            total_questions = int(request.POST.get("total_questions") or 50)
        except (ValueError, TypeError):
            total_questions = 50
            
        try:
            pass_percentage = int(request.POST.get("pass_percentage") or 40)
        except (ValueError, TypeError):
            pass_percentage = 40
            
        external_link = request.POST.get("external_link", "").strip()
        is_active = request.POST.get("is_active") in ["on", "true", "1", True]

        if not title:
            return JsonResponse({"status": "error", "message": "Test title is required."})

        test = OnlineTest.objects.create(
            title=title,
            category=category,
            subtitle=subtitle,
            description=description,
            duration_minutes=duration_minutes,
            total_questions=total_questions,
            pass_percentage=pass_percentage,
            external_link=external_link,
            is_active=is_active
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({
                "status": "success",
                "message": f"Test '{test.title}' created successfully!",
                "test_id": test.id
            })
        return redirect('/admin-dashboard/')

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_update_test_view(request, test_id):
    """
    Updates test details / link from Admin Dashboard.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    test = get_object_or_404(OnlineTest, id=test_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        if not title:
            return JsonResponse({"status": "error", "message": "Test title is required."})

        test.title = title
        test.category = request.POST.get("category", "").strip() or test.category
        test.subtitle = request.POST.get("subtitle", "").strip() or test.subtitle
        test.description = request.POST.get("description", "").strip()
        
        try:
            test.duration_minutes = int(request.POST.get("duration_minutes") or test.duration_minutes)
        except (ValueError, TypeError):
            pass
            
        try:
            test.total_questions = int(request.POST.get("total_questions") or test.total_questions)
        except (ValueError, TypeError):
            pass
            
        try:
            test.pass_percentage = int(request.POST.get("pass_percentage") or test.pass_percentage)
        except (ValueError, TypeError):
            pass
            
        test.external_link = request.POST.get("external_link", "").strip()
        
        status_val = request.POST.get("is_active")
        if status_val is not None:
            test.is_active = status_val in ['true', 'on', '1', True]
            
        test.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({
                "status": "success",
                "message": f"Test '{test.title}' updated successfully!",
                "test_id": test.id,
                "title": test.title,
                "category": test.category,
                "external_link": test.external_link,
                "is_active": test.is_active
            })
        return redirect('/admin-dashboard/')

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_delete_test_view(request, test_id):
    """
    Deletes an online test and all its questions.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            test = OnlineTest.objects.get(id=test_id)
            title = test.title
            test.delete()
            return JsonResponse({"status": "success", "message": f"Test '{title}' deleted successfully!"})
        except OnlineTest.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Test not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_toggle_test_status_view(request, test_id):
    """
    Quickly toggles Active/Inactive status of a test.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            test = OnlineTest.objects.get(id=test_id)
            test.is_active = not test.is_active
            test.save()
            return JsonResponse({
                "status": "success", 
                "message": f"Test status updated to {'Active' if test.is_active else 'Inactive'}.",
                "is_active": test.is_active
            })
        except OnlineTest.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Test not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_add_question_view(request, test_id):
    """
    Adds a new MCQ question to an existing test.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    test = get_object_or_404(OnlineTest, id=test_id)

    if request.method == "POST":
        question_text = request.POST.get("question_text", "").strip()
        option_a = request.POST.get("option_a", "").strip()
        option_b = request.POST.get("option_b", "").strip()
        option_c = request.POST.get("option_c", "").strip()
        option_d = request.POST.get("option_d", "").strip()
        correct_option = request.POST.get("correct_option", "A").strip().upper()
        explanation = request.POST.get("explanation", "").strip()

        if not question_text or not option_a or not option_b or not option_c or not option_d:
            return JsonResponse({"status": "error", "message": "Please fill question and all 4 options."})

        if correct_option not in ['A', 'B', 'C', 'D']:
            correct_option = 'A'

        order = test.questions.count() + 1
        question = QuizQuestion.objects.create(
            test=test,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            explanation=explanation,
            order=order
        )

        return JsonResponse({
            "status": "success",
            "message": "Question added successfully!",
            "question_id": question.id,
            "total_questions": test.questions.count()
        })

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_delete_question_view(request, question_id):
    """
    Deletes an individual question from a test.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            q = QuizQuestion.objects.get(id=question_id)
            test_id = q.test_id
            q.delete()
            total = QuizQuestion.objects.filter(test_id=test_id).count()
            return JsonResponse({
                "status": "success", 
                "message": "Question deleted successfully!",
                "total_questions": total
            })
        except QuizQuestion.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Question not found."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@login_required(login_url='login')
def admin_get_test_questions_view(request, test_id):
    """
    Returns JSON list of questions for a test for the admin modal.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    test = get_object_or_404(OnlineTest, id=test_id)
    questions = test.questions.all().order_by('order', 'id')
    
    data = []
    for idx, q in enumerate(questions, start=1):
        data.append({
            "id": q.id,
            "number": idx,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "correct_option": q.correct_option,
            "explanation": q.explanation or ""
        })

    return JsonResponse({
        "status": "success",
        "test_title": test.title,
        "test_id": test.id,
        "questions": data
    })

