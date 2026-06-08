import os
import django

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# ==========================================
# ENTER YOUR LIVE MYSQL DATABASE DETAILS HERE
# ==========================================
os.environ['DB_NAME'] = 'your_live_db_name'
os.environ['DB_USER'] = 'your_live_db_user'
os.environ['DB_PASSWORD'] = 'your_live_db_password'
os.environ['DB_HOST'] = 'your_live_db_host_ip_or_url'
os.environ['DB_PORT'] = '3306'  # Usually 3306

django.setup()

from django.contrib.auth.models import User

# Details for the admin account you want to create
admin_username = 'admin'
admin_email = 'admin@teachmantra.com'
admin_password = 'Password123!'  # Enter the password you want here

try:
    if User.objects.filter(username=admin_username).exists():
        user = User.objects.get(username=admin_username)
        user.set_password(admin_password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"SUCCESS: Admin user '{admin_username}' already exists. Password updated to '{admin_password}'.")
    else:
        User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)
        print(f"SUCCESS: Admin user '{admin_username}' created successfully with password '{admin_password}'!")
except Exception as e:
    print(f"ERROR connecting to database: {e}")
