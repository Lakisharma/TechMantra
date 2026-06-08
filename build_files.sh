# build_files.sh
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Creating default superuser if not exists..."
python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@teachmantra.com', 'Admin@123')
    print('Superuser admin created successfully!')
else:
    print('Superuser admin already exists.')
"
echo "Build complete!"
