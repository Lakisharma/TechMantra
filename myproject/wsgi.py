"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_wsgi_application()
app = application

# Run database migrations and create admin on startup
try:
    from django.core.management import call_command
    print("Running startup database migrations...")
    call_command('migrate', interactive=False)
    
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@techmantra.com', 'Adminpassword123!')
        print("Startup: Superuser 'admin' created successfully!")
    else:
        # Just in case, ensure the password is set correctly to 'Adminpassword123!'
        admin_user = User.objects.get(username='admin')
        admin_user.set_password('Adminpassword123!')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Startup: Superuser 'admin' password synchronized!")
except Exception as e:
    print(f"Startup database initialization error: {e}")

