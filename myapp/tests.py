from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import StudentProfile

class StudentPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.logout_url = reverse('logout')

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_success(self):
        response = self.client.post(self.register_url, {
            'username': 'teststudent',
            'email': 'test@student.com',
            'password': 'password123',
            'phone': '1234567890',
            'course': 'SSC CGL Coaching Program',
            'full_name': 'Test Student'
        })
        self.assertEqual(response.status_code, 302) # Redirects to profile page
        
        # Verify user and profile creation
        user = User.objects.get(username='teststudent')
        self.assertEqual(user.email, 'test@student.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'Student')
        
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.phone, '1234567890')
        self.assertEqual(profile.course, 'SSC CGL Coaching Program')

    def test_login_post_success(self):
        # Create user and profile first
        user = User.objects.create_user(username='teststudent', password='password123')
        StudentProfile.objects.create(user=user, phone='1234567890', course='SSC CGL Coaching Program')

        # Test login
        response = self.client.post(self.login_url, {
            'username': 'teststudent',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302) # Redirects to profile page

    def test_login_post_invalid(self):
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_profile_unauthorized(self):
        response = self.client.get(self.profile_url)
        # Should redirect to login page
        self.assertRedirects(response, f"{self.login_url}?next={self.profile_url}")

    def test_profile_authorized(self):
        user = User.objects.create_user(username='teststudent', password='password123')
        StudentProfile.objects.create(user=user, phone='1234567890', course='SSC CGL Coaching Program')
        
        self.client.login(username='teststudent', password='password123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_forgot_password_get(self):
        forgot_url = reverse('forgot_password')
        response = self.client.get(forgot_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot_password.html')

    def test_forgot_password_post_success(self):
        user = User.objects.create_user(username='teststudent', email='test@student.com', password='password123')
        StudentProfile.objects.create(user=user, phone='1234567890', course='SSC CGL Coaching Program')
        
        forgot_url = reverse('forgot_password')
        response = self.client.post(forgot_url, {
            'identity': 'teststudent'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password reset successfully!")
        
        user.refresh_from_db()
        self.assertTrue(user.check_password('TM-Reset123'))

    def test_forgot_password_post_invalid(self):
        forgot_url = reverse('forgot_password')
        response = self.client.post(forgot_url, {
            'identity': 'nonexistentuser'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No account found")

    def test_profile_photo_upload_success(self):
        user = User.objects.create_user(username='teststudent', password='password123')
        StudentProfile.objects.create(user=user, phone='1234567890', course='SSC CGL Coaching Program')
        
        self.client.login(username='teststudent', password='password123')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test_avatar.png'
        file.seek(0)
        
        uploaded_file = SimpleUploadedFile(file.name, file.read(), content_type='image/png')
        
        response = self.client.post(self.profile_url, {
            'photo': uploaded_file,
            'ajax': 'true'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile photo updated successfully!")
        
        profile = StudentProfile.objects.get(user=user)
        self.assertTrue(bool(profile.photo))
        self.assertTrue(profile.photo.name.endswith('.png'))
        
        if profile.photo:
            profile.photo.delete(save=False)

    def test_admin_dashboard_unauthorized(self):
        admin_url = reverse('admin_dashboard')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 302)
        
        user = User.objects.create_user(username='studentuser', password='password123')
        self.client.login(username='studentuser', password='password123')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_authorized(self):
        admin_url = reverse('admin_dashboard')
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_admin_update_student(self):
        student_user = User.objects.create_user(username='teststudent', password='password123')
        profile = StudentProfile.objects.create(user=student_user, phone='1234567890', course='SSC CGL Coaching Program')
        
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        
        file = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(100, 100, 100))
        image.save(file, 'jpeg')
        file.name = 'admin_uploaded.jpg'
        file.seek(0)
        
        uploaded_image = SimpleUploadedFile(file.name, file.read(), content_type='image/jpeg')
        
        update_url = reverse('admin_update_student', kwargs={'profile_id': profile.id})
        response = self.client.post(update_url, {
            'username': 'updatedusername',
            'full_name': 'Updated StudentName',
            'email': 'updated@student.com',
            'phone': '9999999999',
            'course': 'Bank PO Prep Course',
            'rank': 'AIR 100',
            'grade': 'A',
            'password': 'newpassword123',
            'status': 'inactive',
            'photo': uploaded_image,
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student profile updated successfully!")
        
        student_user.refresh_from_db()
        self.assertEqual(student_user.username, 'updatedusername')
        self.assertEqual(student_user.first_name, 'Updated')
        self.assertEqual(student_user.last_name, 'StudentName')
        self.assertEqual(student_user.email, 'updated@student.com')
        self.assertFalse(student_user.is_active)
        self.assertTrue(student_user.check_password('newpassword123'))
        
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '9999999999')
        self.assertEqual(profile.course, 'Bank PO Prep Course')
        self.assertEqual(profile.rank, 'AIR 100')
        self.assertEqual(profile.grade, 'A')
        self.assertTrue(bool(profile.photo))
        
        # Clean up
        profile.photo.delete(save=False)

    def test_admin_add_student(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        
        file = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(0, 200, 0))
        image.save(file, 'jpeg')
        file.name = 'admin_added.jpg'
        file.seek(0)
        
        uploaded_image = SimpleUploadedFile(file.name, file.read(), content_type='image/jpeg')
        
        add_student_url = reverse('admin_add_student')
        response = self.client.post(add_student_url, {
            'username': 'newlyaddedstudent',
            'full_name': 'Added StudentName',
            'email': 'addedstudent@test.com',
            'phone': '9876543210',
            'course': 'RRB NTPC Coaching',
            'password': 'addedpassword123',
            'rank': 'AIR 500',
            'grade': 'B+',
            'photo': uploaded_image,
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student account created successfully!")
        
        user = User.objects.get(username='newlyaddedstudent')
        self.assertEqual(user.first_name, 'Added')
        self.assertEqual(user.last_name, 'StudentName')
        self.assertEqual(user.email, 'addedstudent@test.com')
        self.assertTrue(user.check_password('addedpassword123'))
        
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.phone, '9876543210')
        self.assertEqual(profile.course, 'RRB NTPC Coaching')
        self.assertEqual(profile.rank, 'AIR 500')
        self.assertEqual(profile.grade, 'B+')
        self.assertTrue(bool(profile.photo))
        
        # Clean up
        profile.photo.delete(save=False)

    def test_admin_update_settings(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')

        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        from .models import WebsiteSettings

        file = io.BytesIO()
        image = Image.new('RGB', size=(150, 40), color=(0, 0, 255))
        image.save(file, 'png')
        file.name = 'test_logo.png'
        file.seek(0)

        uploaded_logo = SimpleUploadedFile(file.name, file.read(), content_type='image/png')

        update_settings_url = reverse('admin_update_settings')
        response = self.client.post(update_settings_url, {
            'site_name': 'TechMantra Academy Pro',
            'contact_email': 'pro@techmantra.com',
            'contact_phone': '+91 99999 88888',
            'contact_address': 'New Delhi, India',
            'site_logo': uploaded_logo,
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Website settings updated successfully!")

        settings = WebsiteSettings.objects.get(id=1)
        self.assertEqual(settings.site_name, 'TechMantra Academy Pro')
        self.assertEqual(settings.contact_email, 'pro@techmantra.com')
        self.assertEqual(settings.contact_phone, '+91 99999 88888')
        self.assertEqual(settings.contact_address, 'New Delhi, India')
        self.assertTrue(bool(settings.site_logo))

        # Clean up logo image
        settings.site_logo.delete(save=False)

    def test_admin_approve_admission(self):
        from .models import Admission
        admission = Admission.objects.create(name='New Candidate', email='candidate@test.com', phone='9876543210', course='Bank PO Prep Course')
        
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        approve_url = reverse('admin_approve_admission', kwargs={'admission_id': admission.id})
        response = self.client.post(approve_url, {
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admission approved!")
        
        self.assertFalse(Admission.objects.filter(id=admission.id).exists())
        new_user = User.objects.get(username='new_candidate')
        self.assertEqual(new_user.email, 'candidate@test.com')
        
        new_profile = StudentProfile.objects.get(user=new_user)
        self.assertEqual(new_profile.phone, '9876543210')
        self.assertEqual(new_profile.course, 'Bank PO Prep Course')

    def test_admin_delete_record(self):
        student_user = User.objects.create_user(username='teststudent', password='password123')
        profile = StudentProfile.objects.create(user=student_user, phone='1234567890', course='SSC CGL Coaching Program')
        
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        delete_url = reverse('admin_delete_record', kwargs={'record_type': 'student', 'record_id': profile.id})
        response = self.client.post(delete_url, {
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Record deleted successfully!")
        
        self.assertFalse(StudentProfile.objects.filter(id=profile.id).exists())
        self.assertFalse(User.objects.filter(id=student_user.id).exists())

    def test_admin_add_course(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        from .models import Course
        
        file = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(0, 155, 0))
        image.save(file, 'jpeg')
        file.name = 'test_course.jpg'
        file.seek(0)
        
        uploaded_image = SimpleUploadedFile(file.name, file.read(), content_type='image/jpeg')
        
        add_url = reverse('admin_add_course')
        response = self.client.post(add_url, {
            'title': 'Test Course Program',
            'duration': '3 Months',
            'fee': '4500',
            'description': 'Test course description',
            'image': uploaded_image,
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course added successfully!")
        
        course = Course.objects.get(title='Test Course Program')
        self.assertEqual(course.duration, '3 Months')
        self.assertEqual(course.fee, 4500)
        self.assertEqual(course.description, 'Test course description')
        self.assertTrue(bool(course.image))
        
        # Clean up
        course.image.delete(save=False)

    def test_admin_delete_course(self):
        from .models import Course
        course = Course.objects.create(title='Course To Delete', duration='1 Month', fee=2000, description='To delete')
        
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        delete_url = reverse('admin_delete_course', kwargs={'course_id': course.id})
        response = self.client.post(delete_url, {
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course deleted successfully!")
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_admin_add_gallery(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        from .models import GalleryImage
        
        file = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(0, 0, 155))
        image.save(file, 'jpeg')
        file.name = 'test_gallery.jpg'
        file.seek(0)
        
        uploaded_image = SimpleUploadedFile(file.name, file.read(), content_type='image/jpeg')
        
        add_url = reverse('admin_add_gallery')
        response = self.client.post(add_url, {
            'title': 'Test Gallery Picture',
            'category': 'events',
            'image': uploaded_image,
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gallery image uploaded successfully!")
        
        img = GalleryImage.objects.get(title='Test Gallery Picture')
        self.assertEqual(img.category, 'events')
        self.assertTrue(bool(img.image))
        
        # Clean up
        img.image.delete(save=False)

    def test_admin_delete_gallery(self):
        from .models import GalleryImage
        # Create image file
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        
        file = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(155, 155, 0))
        image.save(file, 'jpeg')
        file.name = 'to_delete.jpg'
        file.seek(0)
        uploaded_image = SimpleUploadedFile(file.name, file.read(), content_type='image/jpeg')
        
        img = GalleryImage.objects.create(title='Image To Delete', category='classrooms', image=uploaded_image)
        
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')
        
        delete_url = reverse('admin_delete_gallery', kwargs={'image_id': img.id})
        response = self.client.post(delete_url, {
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gallery image deleted successfully!")
        self.assertFalse(GalleryImage.objects.filter(id=img.id).exists())

    def test_admin_add_admin_success(self):
        from .models import AdminProfile
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')

        add_url = reverse('admin_add_admin')
        response = self.client.post(add_url, {
            'username': 'newstaff',
            'full_name': 'New Staff Member',
            'email': 'newstaff@techmantra.com',
            'password': 'StaffPassword123!',
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin account created successfully!")

        new_user = User.objects.get(username='newstaff')
        self.assertTrue(new_user.is_staff)
        
        profile = AdminProfile.objects.get(user=new_user)
        self.assertEqual(profile.created_by, admin_user)

    def test_admin_delete_admin_success(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        other_staff = User.objects.create_user(username='otherstaff', password='password123', is_staff=True)
        self.client.login(username='adminuser', password='password123')

        delete_url = reverse('admin_delete_admin', kwargs={'admin_id': other_staff.id})
        response = self.client.post(delete_url, {
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin account deleted successfully!")
        self.assertFalse(User.objects.filter(id=other_staff.id).exists())

    def test_admin_delete_admin_self_fail(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        self.client.login(username='adminuser', password='password123')

        delete_url = reverse('admin_delete_admin', kwargs={'admin_id': admin_user.id})
        response = self.client.post(delete_url, {
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You cannot delete your own account.")
        self.assertTrue(User.objects.filter(id=admin_user.id).exists())

    def test_admin_change_admin_password_success(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='password123')
        other_staff = User.objects.create_user(username='otherstaff', password='password123', is_staff=True)
        self.client.login(username='adminuser', password='password123')

        change_url = reverse('admin_change_admin_password', kwargs={'admin_id': other_staff.id})
        response = self.client.post(change_url, {
            'password': 'NewSecurePassword123!',
            'ajax': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "updated successfully!")

        other_staff.refresh_from_db()
        self.assertTrue(other_staff.check_password('NewSecurePassword123!'))




