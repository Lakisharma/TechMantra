from .models import WebsiteSettings

def site_settings(request):
    settings, created = WebsiteSettings.objects.get_or_create(
        id=1,
        defaults={
            "site_name": "TechMantra",
            "contact_email": "info@techmantra.com",
            "contact_phone": "+91 98765 43210",
            "contact_address": "Academy Address, Delhi, India"
        }
    )
    return {"site_settings": settings}
