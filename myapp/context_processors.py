from .models import WebsiteSettings

def site_settings(request):
    settings, created = WebsiteSettings.objects.get_or_create(
        id=1,
        defaults={
            "site_name": "TeachMANTRA",
            "contact_email": "theteachmantra@gmail.com",
            "contact_phone": "+91 98765 43210",
            "contact_address": "Academy Address, Delhi, India"
        }
    )
    if not created:
        needs_save = False
        if settings.site_name == "TechMantra":
            settings.site_name = "TeachMANTRA"
            needs_save = True
        if settings.contact_email in ["info@teachmantra.com", "info@theteachmantra.com", "support@teachmantra.com"]:
            settings.contact_email = "theteachmantra@gmail.com"
            needs_save = True
        if needs_save:
            settings.save()
    return {"site_settings": settings}
