from django.shortcuts import render
from django.http import JsonResponse
from .models import Services, Admission, ContactMessage, StudentProfile, Course, GalleryImage, WebsiteSettings, AdminProfile

# Create your views here.
def index(request):
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
            
    return render(request, 'index.html', {"success_msg": success_msg})

def about(request):
    return render(request, 'about.html')

def courses(request):
    courses_list = Course.objects.all().order_by('-created_at')
    return render(request, 'courses.html', {"courses": courses_list})

def faculty(request):
    return render(request, 'faculty.html')

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

def verify_certificate(request):
    cert_db = {
        "TM-2026-101": {
            "id": "TM-2026-101",
            "name": "Ankit Kumar",
            "course": "SSC CGL Coaching Program",
            "rank": "AIR 45",
            "duration": "6 Months",
            "issue_date": "May 15, 2026",
            "grade": "A+"
        },
        "TM-2026-102": {
            "id": "TM-2026-102",
            "name": "Priya Sharma",
            "course": "Bank PO Prep Course",
            "rank": "AIR 78",
            "duration": "6 Months",
            "issue_date": "May 18, 2026",
            "grade": "A+"
        },
        "TM-2026-103": {
            "id": "TM-2026-103",
            "name": "Rahul Verma",
            "course": "RRB NTPC Coaching",
            "rank": "AIR 29",
            "duration": "6 Months",
            "issue_date": "May 20, 2026",
            "grade": "A+"
        },
        "TM-2026-104": {
            "id": "TM-2026-104",
            "name": "Neha Singh",
            "course": "NDA / CDS Exam Prep",
            "rank": "AIR 15",
            "duration": "1 Year",
            "issue_date": "May 22, 2026",
            "grade": "A++"
        }
    }
    
    cert_id = request.GET.get("cert_id") or request.POST.get("cert_id")
    searched = False
    found = False
    details = None
    
    if cert_id:
        searched = True
        cert_id = cert_id.strip().upper()
        if cert_id in cert_db:
            found = True
            details = cert_db[cert_id]
            
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
    if request.user.is_authenticated:
        return redirect('profile')
        
    courses_list = [
        "SSC CGL Coaching Program",
        "Bank PO Prep Course",
        "RRB NTPC Coaching",
        "NDA / CDS Exam Prep"
    ]
    
    if request.method == "POST":
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
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list})
            
        if User.objects.filter(username=username).exists():
            msg = "Username already exists."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list})
            
        if User.objects.filter(email=email).exists():
            msg = "Email already registered."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list})
            
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
            return JsonResponse({"status": "success", "message": "Registration successful!", "redirect_url": "/profile/"})
        return redirect('profile')
        
    return render(request, 'register.html', {"courses": courses_list})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if not username or not password:
            msg = "Please provide both username and password."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'login.html', {"error_msg": msg})
            
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "success", "message": "Login successful!", "redirect_url": "/profile/"})
            return redirect('profile')
        else:
            msg = "Invalid username or password."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'login.html', {"error_msg": msg})
            
    return render(request, 'login.html')


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
            
    # Try to find a matching certificate in the static certificate database (for demo purposes)
    cert_db = {
        "TM-2026-101": "Ankit Kumar",
        "TM-2026-102": "Priya Sharma",
        "TM-2026-103": "Rahul Verma",
        "TM-2026-104": "Neha Singh"
    }
    
    user_fullname = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    matching_cert = None
    
    for cert_id, name in cert_db.items():
        if name.lower() == user_fullname.lower() or request.user.username.lower() in name.lower():
            matching_cert = {
                "id": cert_id,
                "name": name,
                "course": profile.course,
                "rank": profile.rank,
                "grade": profile.grade
            }
            break
            
    return render(request, 'profile.html', {
        "profile": profile,
        "matching_cert": matching_cert
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

    students = StudentProfile.objects.select_related('user').all()
    admissions = Admission.objects.all().order_by('-created_at')
    contacts = ContactMessage.objects.all().order_by('-created_at')
    courses_list = Course.objects.all().order_by('-created_at')
    images_list = GalleryImage.objects.all().order_by('-uploaded_at')

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
    total_admins = admins.count()

    return render(request, 'admin_dashboard.html', {
        "students": students,
        "admissions": admissions,
        "contacts": contacts,
        "courses": courses_list,
        "gallery_images": images_list,
        "admins": admins,
        "debug_info": debug_info,
        "stats": {
            "total_students": total_students,
            "pending_admissions": pending_admissions,
            "contact_messages": contact_messages,
            "total_courses": total_courses,
            "total_images": total_images,
            "total_admins": total_admins
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
            settings.save()
            return JsonResponse({"status": "success", "message": "Website settings updated successfully!"})
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
            Course.objects.create(
                title=title,
                duration=duration,
                fee=fee_val,
                description=description,
                image=image
            )
            return JsonResponse({"status": "success", "message": "Course added successfully!"})
        except ValueError:
            return JsonResponse({"status": "error", "message": "Fee must be a valid number."})

    return JsonResponse({"status": "error", "message": "Invalid method."})


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


@login_required(login_url='login')
def admin_add_gallery_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        image = request.FILES.get("image")

        if not title or not category or not image:
            return JsonResponse({"status": "error", "message": "Please fill all fields and select an image."})

        GalleryImage.objects.create(
            title=title,
            category=category,
            image=image
        )
        return JsonResponse({"status": "success", "message": "Gallery image uploaded successfully!"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


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





