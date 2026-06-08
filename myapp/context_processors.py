from .models import WebsiteSettings

def site_settings(request):
    settings, created = WebsiteSettings.objects.get_or_create(
        id=1,
        defaults={
            "site_name": "TeachMANTRA",
            "contact_email": "info@teachmantra.com",
            "contact_phone": "+91 98765 43210",
            "contact_address": "Academy Address, Delhi, India"
        }
    )
    if not created and settings.site_name == "TechMantra":
        settings.site_name = "TeachMANTRA"
        settings.save()
    return {"site_settings": settings}
