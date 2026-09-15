import threading
import logging
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import WebsiteSettings

logger = logging.getLogger(__name__)

def _send_email_thread(subject, text_content, html_content, to_email):
    """
    Background worker thread to dispatch SMTP email without blocking HTTP responses.
    """
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'TeachMANTRA Academy <theteachmantra@gmail.com>')
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Welcome email successfully sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")


def send_welcome_registration_email(name, email, course, phone=None, username=None, is_portal_account=False, request=None):
    """
    Sends a high-converting, professional, beautifully styled welcome email
    to the student when their registration/admission is successful.
    """
    if not email:
        return

    # Fetch website settings if available
    try:
        site_settings = WebsiteSettings.objects.first()
        site_name = site_settings.site_name if site_settings and site_settings.site_name else "TeachMANTRA"
        site_phone = site_settings.contact_phone if site_settings and site_settings.contact_phone else "+91 98765 43210"
        site_email = site_settings.contact_email if site_settings and site_settings.contact_email else "theteachmantra@gmail.com"
        site_address = site_settings.contact_address if site_settings and site_settings.contact_address else "TeachMANTRA Academy, India"
    except Exception:
        site_name = "TeachMANTRA"
        site_phone = "+91 98765 43210"
        site_email = "theteachmantra@gmail.com"
        site_address = "TeachMANTRA Academy, India"

    # Base URL for dynamic links
    base_url = "https://theteachmantra.com"
    if request:
        try:
            scheme = 'https' if request.is_secure() else 'http'
            base_url = f"{scheme}://{request.get_host()}"
        except Exception:
            pass

    subject = "Welcome to TeachMANTRA – Congratulations on Joining Us!"
    reg_date = datetime.now().strftime("%d %B %Y, %I:%M %p")
    phone_display = phone if phone else "Not Provided"
    course_display = course if course else "General Competitive & Academic Coaching"
    
    account_info_html = ""
    account_info_text = ""
    if username:
        account_info_html = f"""
        <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">Portal Username:</td>
            <td style="padding: 10px 15px; color: #0f172a; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 700;">{username}</td>
        </tr>
        """
        account_info_text = f"\n• Portal Username: {username}"

    # Plain text content fallback
    text_content = f"""
=====================================================
WELCOME TO {site_name.upper()} ACADEMY!
=====================================================

Dear {name},

Congratulations on Joining Us! Your registration with TeachMANTRA Academy has been successfully received and confirmed.

We are delighted to welcome you to our learning community. Whether you are aiming for government competitive examinations, academic excellence, or specialized skill development, our expert faculty and modern learning portal are here to empower you every step of the way.

-----------------------------------------------------
YOUR REGISTRATION DETAILS:
-----------------------------------------------------
• Student Name: {name}
• Registered Email: {email}
• Mobile Number: {phone_display}
• Selected Course / Plan: {course_display}{account_info_text}
• Registration Date: {reg_date}
• Registration Status: Confirmed & Active

-----------------------------------------------------
WHAT YOU GET WITH TEACHMANTRA:
-----------------------------------------------------
1. Live Online Mock Tests & Instant Evaluation
2. Expert Faculty Mentorship & Doubt Clearing Sessions
3. Comprehensive Study Material & Syllabus Guides
4. Real-Time Performance Analytics & All-India Level Benchmarking

Visit Website & Start Learning:
{base_url}/tests/

Need assistance? Feel free to contact our support team:
Phone: {site_phone}
Email: {site_email}
Address: {site_address}

Best Wishes for Your Success,
Team TeachMANTRA Academy
One Vision, Many Paths to Excellence
=====================================================
"""

    # HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to TeachMANTRA</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      color: #334155;
    }}
    .email-wrapper {{
      max-width: 620px;
      margin: 30px auto;
      background: #ffffff;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
      border: 1px solid #e2e8f0;
    }}
    .email-header {{
      background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #4f46e5 100%);
      padding: 35px 30px 25px 30px;
      text-align: center;
      color: #ffffff;
    }}
    .badge {{
      display: inline-block;
      background: rgba(255, 255, 255, 0.2);
      color: #ffffff;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1px;
      padding: 5px 14px;
      border-radius: 20px;
      margin-bottom: 12px;
      text-transform: uppercase;
    }}
    .email-title {{
      margin: 0;
      font-size: 24px;
      font-weight: 800;
      color: #ffffff;
      line-height: 1.3;
    }}
    .email-subtitle {{
      margin: 8px 0 0 0;
      font-size: 14px;
      color: #cbd5e1;
    }}
    .email-body {{
      padding: 35px 30px;
    }}
    .greeting {{
      font-size: 18px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 12px;
    }}
    .intro-text {{
      font-size: 15px;
      line-height: 1.6;
      color: #475569;
      margin-bottom: 25px;
    }}
    .details-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 25px;
    }}
    .details-header {{
      background: #f1f5f9;
      padding: 12px 18px;
      font-size: 14px;
      font-weight: 700;
      color: #1e293b;
      border-bottom: 1px solid #e2e8f0;
    }}
    .details-table {{
      width: 100%;
      border-collapse: collapse;
    }}
    .feature-card {{
      background: #eff6ff;
      border-left: 4px solid #2563eb;
      padding: 15px 18px;
      border-radius: 0 10px 10px 0;
      margin-bottom: 25px;
    }}
    .feature-title {{
      font-size: 14px;
      font-weight: 700;
      color: #1d4ed8;
      margin-bottom: 6px;
    }}
    .feature-list {{
      margin: 0;
      padding-left: 18px;
      font-size: 13.5px;
      color: #1e40af;
      line-height: 1.6;
    }}
    .cta-btn {{
      display: inline-block;
      background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
      color: #ffffff !important;
      text-decoration: none;
      font-weight: 700;
      font-size: 15px;
      padding: 14px 32px;
      border-radius: 10px;
      text-align: center;
      box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35);
    }}
    .email-footer {{
      background: #f1f5f9;
      padding: 24px 30px;
      text-align: center;
      font-size: 12.5px;
      color: #64748b;
      border-top: 1px solid #e2e8f0;
    }}
    .footer-links {{
      margin-bottom: 10px;
    }}
    .footer-links a {{
      color: #2563eb;
      text-decoration: none;
      margin: 0 8px;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    <!-- Header -->
    <div class="email-header">
      <div class="badge">⭐ Official Registration Confirmation ⭐</div>
      <h1 class="email-title">Welcome to {site_name}!</h1>
      <p class="email-subtitle">Congratulations on Joining Us – One Vision, Many Paths to Excellence</p>
    </div>

    <!-- Body -->
    <div class="email-body">
      <div class="greeting">Dear {name}, 👋</div>
      <p class="intro-text">
        Congratulations on taking this empowering step towards achieving your academic and career goals! We are delighted to confirm that your <strong>registration with {site_name} Academy has been completed successfully</strong>.
      </p>

      <!-- Details Box -->
      <div class="details-box">
        <div class="details-header">
          📋 Registration Details Summary
        </div>
        <table class="details-table">
          <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600; width: 38%;">Student Name:</td>
            <td style="padding: 10px 15px; color: #0f172a; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 700;">{name}</td>
          </tr>
          <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">Email Address:</td>
            <td style="padding: 10px 15px; color: #0f172a; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">{email}</td>
          </tr>
          <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">Contact Number:</td>
            <td style="padding: 10px 15px; color: #0f172a; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">{phone_display}</td>
          </tr>
          <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">Course / Plan:</td>
            <td style="padding: 10px 15px; color: #2563eb; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 700;">{course_display}</td>
          </tr>
          {account_info_html}
          <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; border-bottom: 1px solid #f1f5f9; font-weight: 600;">Registration Date:</td>
            <td style="padding: 10px 15px; color: #0f172a; font-size: 14px; border-bottom: 1px solid #f1f5f9;">{reg_date}</td>
          </tr>
          <tr>
            <td style="padding: 10px 15px; color: #64748b; font-size: 14px; font-weight: 600;">Status:</td>
            <td style="padding: 10px 15px; color: #16a34a; font-size: 14px; font-weight: 700;">✅ Confirmed & Active</td>
          </tr>
        </table>
      </div>

      <!-- Highlights Box -->
      <div class="feature-card">
        <div class="feature-title">🚀 What to Expect Next:</div>
        <ul class="feature-list">
          <li><strong>Live Mock Tests:</strong> Attempt interactive online tests with instant score analysis & detailed solutions.</li>
          <li><strong>Expert Guidance:</strong> Comprehensive study syllabus, proven tricks & dedicated faculty support.</li>
          <li><strong>Counselor Connect:</strong> Our admission coordinator will reach out to help you with your batch schedule.</li>
        </ul>
      </div>

      <!-- Action Button -->
      <div style="text-align: center; margin: 30px 0 10px 0;">
        <a href="{base_url}/tests/" class="cta-btn" target="_blank">
          🎯 Explore Online Mock Tests & Portal &rarr;
        </a>
      </div>
    </div>

    <!-- Footer -->
    <div class="email-footer">
      <div class="footer-links">
        <a href="{base_url}/courses/">Courses</a> &bull;
        <a href="{base_url}/tests/">Online Tests</a> &bull;
        <a href="{base_url}/about/">About Us</a> &bull;
        <a href="{base_url}/contact/">Contact Support</a>
      </div>
      <p style="margin: 6px 0;"><strong>{site_name} Academy</strong> &bull; {site_address}</p>
      <p style="margin: 4px 0;">📞 Helpline: {site_phone} &nbsp;|&nbsp; ✉️ Email: {site_email}</p>
      <p style="margin: 10px 0 0 0; font-size: 11px; color: #94a3b8;">
        This is an automated confirmation email for your recent registration at {site_name}.
      </p>
    </div>
  </div>
</body>
</html>"""

    # Spawn thread for non-blocking email delivery
    t = threading.Thread(
        target=_send_email_thread,
        args=(subject, text_content, html_content, email),
        daemon=True
    )
    t.start()


def send_password_reset_otp_email(name, email, otp_code, request=None):
    """
    Sends a secure 6-digit OTP verification email for account password reset.
    """
    if not email or not otp_code:
        return

    # Fetch website settings if available
    try:
        site_settings = WebsiteSettings.objects.first()
        site_name = site_settings.site_name if site_settings and site_settings.site_name else "TeachMANTRA"
        site_phone = site_settings.contact_phone if site_settings and site_settings.contact_phone else "+91 98765 43210"
        site_email = site_settings.contact_email if site_settings and site_settings.contact_email else "theteachmantra@gmail.com"
        site_address = site_settings.contact_address if site_settings and site_settings.contact_address else "TeachMANTRA Academy, India"
    except Exception:
        site_name = "TeachMANTRA"
        site_phone = "+91 98765 43210"
        site_email = "theteachmantra@gmail.com"
        site_address = "TeachMANTRA Academy, India"

    subject = f"{otp_code} is your {site_name} Password Reset OTP"
    
    text_content = f"""
=====================================================
PASSWORD RESET OTP - {site_name.upper()} ACADEMY
=====================================================

Dear {name},

We received a request to reset your password for your {site_name} Academy account.

Your 6-Digit One-Time Password (OTP) is:
----------------------------------------
>>> {otp_code} <<<
----------------------------------------

This OTP is valid for 10 minutes. Please enter this code on the password reset page to create your new password.

If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.

Best regards,
{site_name} Academy Support Team
Helpline: {site_phone} | Email: {site_email}
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset OTP - {site_name}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #f1f5f9;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
    }}
    .email-wrapper {{
      max-width: 580px;
      margin: 25px auto;
      background: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      border: 1px solid #e2e8f0;
    }}
    .email-header {{
      background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
      padding: 28px 24px;
      text-align: center;
      color: #ffffff;
    }}
    .email-body {{
      padding: 28px 24px;
    }}
    .otp-box {{
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
      border: 2px dashed #6366f1;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      margin: 24px 0;
    }}
    .otp-digits {{
      font-size: 32px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #4338ca;
      font-family: monospace, sans-serif;
    }}
    .email-footer {{
      background-color: #f8fafc;
      padding: 18px 24px;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      border-top: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    <div class="email-header">
      <h1 style="margin: 0; font-size: 22px; font-weight: 800;">{site_name} Academy</h1>
      <p style="margin: 6px 0 0 0; font-size: 14px; opacity: 0.9;">Account Password Reset OTP</p>
    </div>
    
    <div class="email-body">
      <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Dear {name},</h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569;">
        We received a request to reset your password for your <strong>{site_name}</strong> student account. Enter the 6-digit OTP code below to verify your email and create a new password:
      </p>

      <div class="otp-box">
        <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #6366f1; margin-bottom: 8px;">
          Your 6-Digit OTP Code
        </div>
        <div class="otp-digits">{otp_code}</div>
        <div style="font-size: 12px; color: #64748b; margin-top: 8px;">
          ⏰ Valid for 10 minutes
        </div>
      </div>

      <p style="font-size: 13px; line-height: 1.5; color: #64748b; margin-bottom: 0;">
        If you did not request this, please disregard this email. Your password will remain unchanged.
      </p>
    </div>

    <div class="email-footer">
      <p style="margin: 4px 0;"><strong>{site_name} Academy</strong> &bull; {site_address}</p>
      <p style="margin: 4px 0;">Helpline: {site_phone} | Email: {site_email}</p>
    </div>
  </div>
</body>
</html>"""

    t = threading.Thread(
        target=_send_email_thread,
        args=(subject, text_content, html_content, email),
        daemon=True
    )
    t.start()
