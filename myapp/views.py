import json
import csv
from django.db import models
from django.db.models import Q, Avg, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import (
    Services, Admission, ContactMessage, StudentProfile, Course, 
    GalleryImage, TeamMember, WebsiteSettings, AdminProfile, Certificate, 
    BroadcastEmail, OnlineTest, QuizQuestion, TestSubmission, TopperResult
)
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, date
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
    populate_default_courses()
    courses_list = Course.objects.all().order_by('id')
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
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        course = request.POST.get("course", "").strip()
        message = request.POST.get("message", "").strip()
        
        if not (name and email and phone and course):
            msg = "Please fill all required fields."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'admissions.html', {"success_msg": f"Error: {msg}"})
            
        clean_phone = ''.join(c for c in phone if c.isdigit())
        if len(clean_phone) != 10:
            msg = "Please enter a valid 10-digit mobile number (numbers only)."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'admissions.html', {"success_msg": f"Error: {msg}"})
            
        adm = Admission.objects.create(
            name=name,
            email=email,
            phone=clean_phone,
            course=course,
            message=message
        )
        
        # If student is logged in, link course to profile
        if request.user.is_authenticated:
            try:
                profile, _ = StudentProfile.objects.get_or_create(user=request.user)
                profile.course = course
                if clean_phone and (profile.phone == "N/A" or not profile.phone):
                    profile.phone = clean_phone
                profile.save()
            except Exception:
                pass
                
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({"status": "success", "message": f"Admission registration submitted successfully for {course}!"})
        success_msg = f"Admission registration submitted successfully for {course}!"
            
    return render(request, 'admissions.html', {"success_msg": success_msg})

def gallery(request):
    images_list = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'gallery.html', {"images": images_list})

def results(request):
    populate_default_toppers()
    toppers_list = TopperResult.objects.all().order_by('order', 'id')
    return render(request, 'results.html', {"toppers": toppers_list})

def contact(request):
    success_msg = None
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()
        
        if not (name and email and phone and message):
            msg = "Please fill all required fields."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'contact.html', {"success_msg": f"Error: {msg}"})
            
        clean_phone = ''.join(c for c in phone if c.isdigit())
        if len(clean_phone) != 10:
            msg = "Please enter a valid 10-digit mobile number (numbers only)."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'contact.html', {"success_msg": f"Error: {msg}"})
            
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=clean_phone,
            message=message
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({"status": "success", "message": "Message sent successfully!"})
        success_msg = "Message sent successfully!"
            
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

def parse_quiz_html(html_content):
    """
    Parses an HTML quiz file or raw content containing JS DATA array
    or HTML questions, returns (title, category, questions_list).
    """
    import re, json
    
    title = None
    category = "Mixed General Studies"
    
    # 1. Try finding title from <title> or <h1>
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        raw_t = title_match.group(1).replace('TeachMANTRA', '').replace('|', '').replace('—', '-').strip()
        if raw_t:
            title = raw_t
    if not title:
        h1_match = re.search(r'<h1>(.*?)</h1>', html_content, re.IGNORECASE)
        if h1_match:
            title = h1_match.group(1).replace('—', '-').strip()
            
    # Try finding category from header text
    cat_match = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.IGNORECASE)
    if cat_match:
        p_text = re.sub(r'<[^>]+>', '', cat_match.group(1)).replace('⚡️', '').replace('|', '').strip()
        if p_text:
            category = p_text
            
    # 2. Extract DATA array
    data_match = re.search(r'(?:const|let|var)\s+DATA\s*=\s*(\[\s*\{.*?\}\s*\])\s*;', html_content, re.DOTALL)
    if not data_match:
        data_match = re.search(r'DATA\s*=\s*(\[.*?\])\s*;', html_content, re.DOTALL)
        
    questions = []
    
    if data_match:
        json_str = data_match.group(1)
        try:
            raw_data = json.loads(json_str)
            for idx, item in enumerate(raw_data, start=1):
                q_text = item.get("q", "").strip()
                opts = item.get("o", [])
                ans_idx = item.get("a", 0)
                
                opt_a = opts[0] if len(opts) > 0 else ""
                opt_b = opts[1] if len(opts) > 1 else ""
                opt_c = opts[2] if len(opts) > 2 else ""
                opt_d = opts[3] if len(opts) > 3 else ""
                
                correct_map = ["A", "B", "C", "D"]
                correct_opt = correct_map[ans_idx] if isinstance(ans_idx, int) and 0 <= ans_idx < 4 else "A"
                
                if q_text and opt_a:
                    questions.append({
                        "question_text": q_text,
                        "option_a": opt_a,
                        "option_b": opt_b,
                        "option_c": opt_c,
                        "option_d": opt_d,
                        "correct_option": correct_opt,
                        "explanation": item.get("explanation", ""),
                        "order": idx
                    })
        except Exception:
            pass
            
    return title, category, questions


def populate_default_online_tests():
    if not OnlineTest.objects.filter(title__icontains="DAY 07").exists():
        day7_html = """
        const DATA=[{"q": "वैदिक काल में ‘सभा’ और ‘समिति’ मुख्यतः किससे संबंधित थीं?", "o": ["धार्मिक अनुष्ठान", "प्रशासनिक एवं राजनीतिक संस्थाएँ", "व्यापारिक संगठन", "सैन्य छावनियाँ"], "a": 1}, {"q": "भारत में ‘काली मिट्टी’ का सर्वाधिक संबंध किस फसल से माना जाता है?", "o": ["चाय", "कपास", "जूट", "गेहूँ"], "a": 1}, {"q": "निम्नलिखित में से किस ग्रह का घूर्णन अपनी धुरी पर अन्य अधिकांश ग्रहों की तुलना में विपरीत दिशा में है?", "o": ["मंगल", "बृहस्पति", "शुक्र", "बुध"], "a": 2}, {"q": "भारतीय संविधान का कौन-सा अनुच्छेद ‘कानून के समक्ष समानता’ से संबंधित है?", "o": ["अनुच्छेद 14", "अनुच्छेद 16", "अनुच्छेद 18", "अनुच्छेद 21"], "a": 0}, {"q": "‘संगम साहित्य’ मुख्यतः किस क्षेत्र की प्राचीन संस्कृति से संबंधित है?", "o": ["बंगाल", "तमिल क्षेत्र", "पंजाब", "कश्मीर"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा भारत का प्रमुख लौह-अयस्क क्षेत्र है?", "o": ["सिंहभूम", "कच्छ", "मालवा", "कोंकण"], "a": 0}, {"q": "भारत में ‘राष्ट्रीय आपातकाल’ की घोषणा किन परिस्थितियों में की जा सकती है?", "o": ["केवल वित्तीय संकट में", "युद्ध, बाहरी आक्रमण या सशस्त्र विद्रोह में", "केवल राज्य सरकार की विफलता में", "केवल महामारी के समय"], "a": 1}, {"q": "मानव शरीर में पित्त का निर्माण मुख्यतः कहाँ होता है?", "o": ["अग्न्याशय", "यकृत", "आमाशय", "छोटी आंत"], "a": 1}, {"q": "‘भारत का मैनचेस्टर’ किस शहर को कहा जाता है?", "o": ["कानपुर", "अहमदाबाद", "सूरत", "मुंबई"], "a": 1}, {"q": "‘हरित क्रांति’ के प्रारंभिक चरण में भारत में मुख्यतः किन फसलों के उत्पादन पर जोर दिया गया?", "o": ["चाय और कॉफी", "गेहूँ और चावल", "कपास और जूट", "गन्ना और तंबाकू"], "a": 1}, {"q": "निम्नलिखित में से किस भक्ति संत ने ‘निर्गुण भक्ति’ की धारा को मजबूत किया?", "o": ["सूरदास", "तुलसीदास", "कबीर", "मीराबाई"], "a": 2}, {"q": "‘दीन-ए-इलाही’ की स्थापना किस मुगल शासक से संबंधित है?", "o": ["बाबर", "हुमायूँ", "अकबर", "औरंगजेब"], "a": 2}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. लोकसभा का कार्यकाल सामान्यतः पाँच वर्ष होता है।\\n2. राष्ट्रीय आपातकाल के दौरान लोकसभा का कार्यकाल बढ़ाया जा सकता है।\\n3. लोकसभा का कार्यकाल एक बार में अधिकतम दो वर्ष बढ़ाया जा सकता है।", "o": ["केवल 1", "केवल 1 और 2", "केवल 2 और 3", "1, 2 और 3"], "a": 1}, {"q": "‘मुद्रा’ के निम्नलिखित कार्यों में कौन-सा प्राथमिक कार्य नहीं है?", "o": ["विनिमय का माध्यम", "मूल्य मापने का साधन", "मूल्य संचय", "जनसंख्या नियंत्रण"], "a": 3}, {"q": "‘प्रायद्वीपीय भारत’ की अधिकांश नदियों की एक प्रमुख विशेषता क्या है?", "o": ["वे सदैव हिमनदों से पोषित होती हैं", "उनमें वर्षा पर निर्भरता अधिक होती है", "वे केवल उत्तर दिशा में बहती हैं", "वे सभी बारहमासी हैं"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा विटामिन दृष्टि से संबंधित है?", "o": ["विटामिन A", "विटामिन B12", "विटामिन K", "विटामिन D"], "a": 0}, {"q": "‘इलाहाबाद प्रशस्ति’ किस शासक की उपलब्धियों की जानकारी देती है?", "o": ["चंद्रगुप्त मौर्य", "समुद्रगुप्त", "स्कंदगुप्त", "हर्षवर्धन"], "a": 1}, {"q": "भारत में ‘सहकारी समितियों’ को संवैधानिक महत्व किस संविधान संशोधन से मिला?", "o": ["86वाँ", "91वाँ", "97वाँ", "101वाँ"], "a": 2}, {"q": "निम्नलिखित में से कौन-सा युग्म सही सुमेलित है?", "o": ["नीलगिरि — हिमालय", "अरावली — प्राचीन वलित पर्वत", "सतपुड़ा — नवीन वलित पर्वत", "शिवालिक — दक्कन का पठार"], "a": 1}, {"q": "‘राष्ट्रीय मानवाधिकार आयोग’ भारत में किस वर्ष स्थापित किया गया था?", "o": ["1989", "1993", "1998", "2001"], "a": 1}, {"q": "‘इक्ता प्रणाली’ का व्यापक प्रयोग दिल्ली सल्तनत में किस उद्देश्य से किया जाता था?", "o": ["धार्मिक शिक्षा", "राजस्व एवं प्रशासनिक व्यवस्था", "समुद्री व्यापार", "मुद्रा निर्माण"], "a": 1}, {"q": "निम्नलिखित में से कौन-सी गैस ‘अम्ल वर्षा’ के निर्माण में महत्वपूर्ण भूमिका निभाती है?", "o": ["सल्फर डाइऑक्साइड", "ऑक्सीजन", "हाइड्रोजन", "हीलियम"], "a": 0}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. लोकसभा अध्यक्ष लोकसभा का पीठासीन अधिकारी होता है।\\n2. अध्यक्ष के निर्वाचन में लोकसभा के सदस्य भाग लेते हैं।\\n3. अध्यक्ष अपने पद से हटने के बाद भी लोकसभा का सदस्य रहना आवश्यक है।", "o": ["केवल 1", "केवल 1 और 2", "केवल 2 और 3", "1, 2 और 3"], "a": 1}, {"q": "‘बैंकों का बैंक’ किसे कहा जाता है?", "o": ["भारतीय स्टेट बैंक", "भारतीय रिजर्व बैंक", "नाबार्ड", "भारतीय स्टॉक एक्सचेंज"], "a": 1}, {"q": "‘पवनों का मौसमी उलटाव’ किस घटना की प्रमुख विशेषता है?", "o": ["ज्वार-भाटा", "मानसून", "भूकंप", "चक्रवात"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा रोग वायरस के कारण होता है?", "o": ["टिटनेस", "पोलियो", "मलेरिया", "हैजा"], "a": 1}, {"q": "‘स्वराज मेरा जन्मसिद्ध अधिकार है’ कथन किससे संबंधित है?", "o": ["गोपाल कृष्ण गोखले", "बाल गंगाधर तिलक", "लाला लाजपत राय", "बिपिन चंद्र पाल"], "a": 1}, {"q": "‘राजकोषीय नीति’ मुख्यतः किससे संबंधित है?", "o": ["मुद्रा आपूर्ति और ब्याज दर", "सरकारी आय और व्यय", "केवल विदेशी मुद्रा", "केवल बैंक ऋण"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा दर्रा भारत और तिब्बत के बीच ऐतिहासिक व्यापार मार्गों में महत्वपूर्ण रहा है?", "o": ["नाथू ला", "पालघाट", "भोर घाट", "थाल घाट"], "a": 0}, {"q": "‘जैव विविधता हॉटस्पॉट’ घोषित किए जाने के लिए किसी क्षेत्र में क्या विशेष महत्व होना चाहिए?", "o": ["केवल अधिक जनसंख्या", "उच्च स्थानिकता और गंभीर आवास क्षति", "केवल अधिक वर्षा", "केवल अधिक खनिज"], "a": 1}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. भारत में राष्ट्रपति शासन अनुच्छेद 356 से संबंधित है।\\n2. राष्ट्रपति शासन लगाए जाने पर राज्य विधानसभा को निलंबित या भंग किया जा सकता है।\\n3. राष्ट्रपति शासन को प्रत्येक छह महीने में संसद की स्वीकृति आवश्यक होती है।", "o": ["केवल 1", "केवल 1 और 2", "केवल 2 और 3", "1, 2 और 3"], "a": 3}, {"q": "‘मौद्रिक आधार’ में सामान्यतः क्या शामिल होता है?", "o": ["केवल जनता की बचत", "प्रचलन में मुद्रा और बैंकों के केंद्रीय बैंक में भंडार", "केवल सरकारी कर", "केवल विदेशी मुद्रा भंडार"], "a": 1}, {"q": "निम्नलिखित में से किस प्रक्रिया में पौधों में जल का ऊपर की ओर परिवहन मुख्यतः पत्तियों से होने वाले जल-वाष्पोत्सर्जन से जुड़ा है?", "o": ["परासरण", "वाष्पोत्सर्जन खिंचाव", "प्रकाश संश्लेषण", "किण्वन"], "a": 1}, {"q": "‘स्थलमंडल’ और ‘अस्थेनोस्फीयर’ के संबंध में कौन-सा कथन सही है?", "o": ["दोनों पृथ्वी के वायुमंडलीय स्तर हैं", "स्थलमंडल कठोर बाहरी परत है और उसके नीचे अपेक्षाकृत कमजोर/लचीली अस्थेनोस्फीयर होती है", "अस्थेनोस्फीयर केवल महासागरों में होती है", "स्थलमंडल केवल कोर का भाग है"], "a": 1}, {"q": "निम्नलिखित में से किसे ‘लोक कल्याणकारी राज्य’ की अवधारणा से सबसे अधिक जोड़ा जाता है?", "o": ["राज्य की पूर्ण निष्क्रियता", "नागरिकों के सामाजिक एवं आर्थिक कल्याण में राज्य की सक्रिय भूमिका", "केवल सैन्य विस्तार", "केवल मुक्त व्यापार"], "a": 1}, {"q": "‘कार्बन मोनोऑक्साइड’ मानव शरीर में मुख्यतः किस प्रकार हानिकारक है?", "o": ["रक्त के हीमोग्लोबिन से जुड़कर ऑक्सीजन वहन क्षमता घटाती है", "हड्डियों को सीधे घोल देती है", "पाचन एंजाइम बढ़ाती है", "रक्त में कैल्शियम बढ़ाती है"], "a": 0}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. राज्यपाल की नियुक्ति राष्ट्रपति करता है।\\n2. राज्यपाल का सामान्य कार्यकाल पाँच वर्ष होता है।\\n3. राज्यपाल को केवल राज्य विधानसभा ही पद से हटा सकती है।", "o": ["केवल 1", "केवल 1 और 2", "केवल 2 और 3", "1, 2 और 3"], "a": 1}, {"q": "‘वास्तविक सकल घरेलू उत्पाद’ और ‘नाममात्र सकल घरेलू उत्पाद’ में मुख्य अंतर किससे संबंधित है?", "o": ["जनसंख्या", "कीमतों के प्रभाव का समायोजन", "भौगोलिक सीमा", "केवल निर्यात"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा ‘अपक्षय’ का उदाहरण है?", "o": ["चट्टानों का अपने स्थान पर टूटना/क्षरण", "नदी द्वारा मिट्टी को दूर ले जाना", "समुद्र द्वारा बालू का निक्षेप", "हवा द्वारा रेत का स्थानांतरण"], "a": 0}, {"q": "‘भारतीय अंतरिक्ष अनुसंधान संगठन’ की स्थापना किस वर्ष हुई थी?", "o": ["1962", "1969", "1975", "1980"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा कथन ‘मांग की लोच’ के संदर्भ में सही है?", "o": ["कीमत में परिवर्तन से मांग में कोई परिवर्तन नहीं होता", "कीमत में परिवर्तन के प्रति मांग की मात्रा की संवेदनशीलता को मांग की कीमत लोच कहा जाता है", "यह केवल सरकारी वस्तुओं पर लागू होती है", "इसका आय से कोई संबंध नहीं"], "a": 1}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. भारत में नियंत्रक एवं महालेखा परीक्षक की रिपोर्ट संसद के समक्ष रखी जाती है।\\n2. CAG संघ और राज्यों के खातों से संबंधित संवैधानिक दायित्व निभाता है।\\n3. CAG की नियुक्ति प्रधानमंत्री करता है।", "o": ["केवल 1", "केवल 1 और 2", "केवल 2 और 3", "1, 2 और 3"], "a": 1}, {"q": "‘समुद्री धाराएँ’ जलवायु को प्रभावित करने में महत्वपूर्ण क्यों हैं?", "o": ["वे केवल समुद्र की गहराई बदलती हैं", "वे ऊष्मा के पुनर्वितरण में सहायता करती हैं", "वे पृथ्वी का घूर्णन रोकती हैं", "वे केवल ज्वार पैदा करती हैं"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा जैव-प्रौद्योगिकी का अनुप्रयोग है?", "o": ["ऊतक संवर्धन", "ज्वार-भाटा", "अपक्षय", "भूकंपीय तरंग"], "a": 0}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. संविधान की प्रस्तावना में ‘समाजवादी’ शब्द मूल संविधान में था।\\n2. ‘समाजवादी’ और ‘पंथनिरपेक्ष’ शब्द 42वें संशोधन द्वारा जोड़े गए।\\n3. ‘अखंडता’ शब्द भी 42वें संशोधन द्वारा जोड़ा गया।", "o": ["केवल 1", "केवल 2", "केवल 2 और 3", "1, 2 और 3"], "a": 2}, {"q": "‘जनगणना’ के संदर्भ में निम्नलिखित में से कौन-सा कथन सही है?", "o": ["भारत में जनगणना प्रत्येक पाँच वर्ष में होती है", "भारत में जनगणना सामान्यतः दस वर्ष के अंतराल पर होती है", "जनगणना केवल ग्रामीण क्षेत्रों में होती है", "जनगणना केवल जन्म-मृत्यु का रिकॉर्ड है"], "a": 1}, {"q": "निम्नलिखित में से कौन-सा पदार्थ सामान्यतः ‘अर्धचालक’ के रूप में प्रयुक्त होता है?", "o": ["सिलिकॉन", "तांबा", "चांदी", "एल्युमिनियम"], "a": 0}, {"q": "‘सार्वजनिक वस्तु’ की अर्थशास्त्रीय अवधारणा में कौन-सी विशेषता महत्वपूर्ण है?", "o": ["केवल निजी उपभोग", "गैर-बहिष्करण और गैर-प्रतिस्पर्धी उपभोग की विशेषता", "केवल अधिक कीमत", "केवल सरकारी स्वामित्व"], "a": 1}, {"q": "निम्नलिखित कथनों पर विचार कीजिए—\\n1. भारत में राष्ट्रीय आय के आधिकारिक अनुमानों से संबंधित प्रमुख सांख्यिकीय कार्य राष्ट्रीय सांख्यिकी कार्यालय करता है।\\n2. सकल घरेलू उत्पाद देश की भौगोलिक सीमा के भीतर उत्पादन को मापता है।\\n3. सकल राष्ट्रीय आय में विदेश से प्राप्त शुद्ध कारक आय का महत्व होता है।", "o": ["केवल 1", "केवल 1 और 2", "केवल 2 और 3", "1, 2 और 3"], "a": 3}, {"q": "निम्नलिखित में से कौन-सा कथन ‘प्लेट विवर्तनिकी’ सिद्धांत को सबसे बेहतर स्पष्ट करता है?", "o": ["पृथ्वी की सभी चट्टानें स्थिर हैं", "स्थलमंडलीय प्लेटें गतिशील हैं और उनकी परस्पर क्रियाओं से भूकंप, ज्वालामुखी एवं पर्वतनिर्माण जैसी घटनाएँ जुड़ी हैं", "केवल महासागर गतिशील हैं", "पृथ्वी का कोर ही सभी भौगोलिक घटनाओं का प्रत्यक्ष कारण है"], "a": 1}];
        """
        _, _, q_list = parse_quiz_html(day7_html)
        if q_list:
            test = OnlineTest.objects.create(
                title="DAY 07 — GS ONLINE QUIZ",
                category="Mixed General Studies",
                subtitle="50 Questions • Mixed General Studies • GS BY VINUS SIR",
                description="TeachMANTRA Academy Daily Practice Online Mock Test with live timer, instant grading, and detailed explanations.",
                duration_minutes=30,
                total_questions=len(q_list),
                pass_percentage=40,
                is_active=True
            )
            for q in q_list:
                QuizQuestion.objects.create(test=test, **q)


def populate_default_courses():
    official_courses = [
        {
            "title": "SSC GD",
            "duration": "6 Months",
            "fee": 3100,
            "description": "Comprehensive coaching for SSC GD Constable Exam covering Reasoning, General Knowledge, Elementary Mathematics, and Hindi/English."
        },
        {
            "title": "AIRFORCE / NAVY (X & Y GROUP)",
            "duration": "6 Months",
            "fee": 3100,
            "description": "Dedicated coaching for Indian Air Force & Navy X & Y Group entrance examinations with written test & physical test guidance."
        },
        {
            "title": "ARMY GD",
            "duration": "6 Months",
            "fee": 3100,
            "description": "Targeted training for Indian Army General Duty written exam, regular practice tests, and physical training guidance."
        },
        {
            "title": "UP POLICE / DELHI POLICE",
            "duration": "6 Months",
            "fee": 2999,
            "description": "Special batch for UP Police Constable & Delhi Police SI/Constable recruitment exams with complete syllabus coverage and test series."
        },
        {
            "title": "UPSSSC / LEKHPAL / VDO / PET",
            "duration": "6 Months",
            "fee": 2999,
            "description": "All-in-one preparation for UPSSSC PET, Lekhpal, VDO, and Junior Assistant state government competitive examinations."
        },
        {
            "title": "TEACHERS PACK ( SUPER TET / CTET / TET )",
            "duration": "6 Months",
            "fee": 2999,
            "description": "Master teaching competitive exams with Super TET, CTET Paper 1 & 2, and UPTET focused pedagogy & subject preparation."
        },
        {
            "title": "RAILWAY NTPC / ALP / GROUP D",
            "duration": "6 Months",
            "fee": 3100,
            "description": "Complete coaching for RRB NTPC, Assistant Loco Pilot (ALP), and Railway Group D exams with mock test practice."
        },
        {
            "title": "NDA / CDS (Defence)",
            "duration": "1 Year",
            "fee": 6100,
            "description": "1-Year comprehensive foundation & advanced program for UPSC NDA & CDS examinations with SSB interview guidance."
        },
        {
            "title": "COMPUTER PACK",
            "duration": "3 Months",
            "fee": 6500,
            "description": "Practical computer skills covering CCC, MS Office, Internet, Graphic basics, and typing skills with certification."
        },
        {
            "title": "SPOKEN ENGLISH PROGRAM",
            "duration": "2 Months",
            "fee": 2500,
            "description": "Intensive 2-Month English communication, vocabulary, grammar, and public speaking confidence-building course."
        }
    ]

    # Clean up any old mock courses
    official_titles = {c["title"].strip().upper() for c in official_courses}
    old_names = [
        "javascript", "css", "html", "python", "python developer",
        "ssc preparation", "banking exam prep", "railway exams",
        "nda / cds prep", "computer courses", "spoken english"
    ]
    for c in Course.objects.all():
        if c.title.strip().lower() in old_names or (c.title.strip().upper() not in official_titles and c.fee in [5000, 6000, 12000, 8000, 4000, 25000]):
            c.delete()

    existing_titles = set(Course.objects.values_list('title', flat=True))
    for c in official_courses:
        if c["title"] not in existing_titles:
            Course.objects.create(
                title=c["title"],
                duration=c["duration"],
                fee=c["fee"],
                description=c["description"]
            )


def populate_default_toppers():
    if not TopperResult.objects.exists():
        defaults = [
            {
                "name": "Sunanda yadav",
                "exam_name": "UP POLICE 2024",
                "rank": "AIR 16753",
                "badge": "Rank 1",
                "order": 1
            },
            {
                "name": "Rahul Pal",
                "exam_name": "UP POLICE 2024",
                "rank": "AIR 22863",
                "badge": "Rank 1",
                "order": 2
            },
            {
                "name": "Rahul Verma",
                "exam_name": "RRB NTPC 2024",
                "rank": "AIR 29",
                "badge": "Rank 1",
                "order": 3
            },
            {
                "name": "Neha Singh",
                "exam_name": "NDA 2024",
                "rank": "AIR 15",
                "badge": "Rank 1",
                "order": 4
            },
        ]
        for d in defaults:
            TopperResult.objects.create(**d)


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
        "SSC GD (₹ 3100)",
        "AIRFORCE / NAVY (X & Y GROUP) (₹ 3100)",
        "ARMY GD (₹ 3100)",
        "UP POLICE / DELHI POLICE (₹ 2999)",
        "UPSSSC / LEKHPAL / VDO / PET (₹ 2999)",
        "TEACHERS PACK ( SUPER TET / CTET / TET ) (₹ 2999)",
        "RAILWAY NTPC / ALP / GROUP D (₹ 3100)",
        "NDA / CDS (Defence) (₹ 6100)",
        "COMPUTER PACK (₹ 6500)",
        "SPOKEN ENGLISH PROGRAM (₹ 2500)",
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
            
        clean_phone = ''.join(c for c in phone if c.isdigit())
        if len(clean_phone) != 10:
            msg = "Please enter a valid 10-digit mobile number (numbers only)."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                return JsonResponse({"status": "error", "message": msg})
            return render(request, 'register.html', {"error_msg": msg, "courses": courses_list, "next": next_url})
        phone = clean_phone
            
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




def parse_course_info(raw_course_str):
    """Parse course name, fee and enrollment details from course string."""
    if not raw_course_str or raw_course_str.strip() in ["N/A", "", "None"]:
        return {
            "title": "General Student",
            "raw": "N/A",
            "fee": "₹ 2,999",
            "duration": "6 Months Classroom + Mock Tests",
            "is_enrolled": False
        }
    
    import re
    raw = raw_course_str.strip()
    title = raw
    fee = None
    
    fee_match = re.search(r'\((?:₹|Rs\.?|INR)?\s*([0-9,]+)\)', raw, re.IGNORECASE)
    if fee_match:
        fee_digits = fee_match.group(1).replace(',', '')
        fee = f"₹ {int(fee_digits):,}"
        title = re.sub(r'\s*\((?:₹|Rs\.?|INR)?\s*[0-9,]+\)', '', raw).strip()
    else:
        c_obj = Course.objects.filter(models.Q(title__iexact=raw) | models.Q(title__icontains=raw)).first()
        if c_obj:
            title = c_obj.title
            fee = f"₹ {c_obj.fee:,}"
        else:
            known_fees = {
                "SSC GD": "₹ 3,100",
                "AIRFORCE": "₹ 3,100",
                "NAVY": "₹ 3,100",
                "ARMY GD": "₹ 3,100",
                "UP POLICE": "₹ 2,999",
                "DELHI POLICE": "₹ 2,999",
                "UPSSSC": "₹ 2,999",
                "LEKHPAL": "₹ 2,999",
                "VDO": "₹ 2,999",
                "PET": "₹ 2,999",
                "TEACHERS PACK": "₹ 2,999",
                "SUPER TET": "₹ 2,999",
                "CTET": "₹ 2,999",
                "TET": "₹ 2,999",
                "RAILWAY NTPC": "₹ 3,100",
                "ALP": "₹ 3,100",
                "GROUP D": "₹ 3,100",
                "NDA": "₹ 6,100",
                "CDS": "₹ 6,100",
                "COMPUTER PACK": "₹ 6,500",
                "SPOKEN ENGLISH": "₹ 2,500",
            }
            for k, v in known_fees.items():
                if k.lower() in raw.lower():
                    fee = v
                    break
            if not fee:
                fee = "₹ 2,999"
                
    return {
        "title": title,
        "raw": raw,
        "fee": fee,
        "duration": "6 Months Classroom + Online Tests",
        "is_enrolled": True
    }


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
    
    # Auto-link admission record if profile course is unassigned
    if profile.course in ["N/A", "", None]:
        user_adm = Admission.objects.filter(
            models.Q(email__iexact=request.user.email) | 
            models.Q(phone=profile.phone) |
            models.Q(name__iexact=user_fullname)
        ).order_by('-created_at').first()
        if user_adm and user_adm.course:
            profile.course = user_adm.course
            profile.save()
            
    course_info = parse_course_info(profile.course)
    
    # User's recent admission application requests (if any)
    my_admissions = Admission.objects.filter(
        models.Q(email__iexact=request.user.email) | 
        models.Q(phone=profile.phone) |
        models.Q(name__iexact=user_fullname)
    ).order_by('-created_at')
    
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

    # Map of test_id -> submission for single-attempt button rendering
    attempted_test_map = {s.test_id: s for s in my_submissions}
            
    return render(request, 'profile.html', {
        "profile": profile,
        "course_info": course_info,
        "my_admissions": my_admissions,
        "matching_cert": matching_cert,
        "available_tests": available_tests,
        "attempted_test_map": attempted_test_map,
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
    populate_default_courses()
    populate_default_toppers()

    students = StudentProfile.objects.select_related('user').all()
    admissions = Admission.objects.all().order_by('-created_at')
    contacts = ContactMessage.objects.all().order_by('-created_at')
    courses_list = Course.objects.all().order_by('id')
    images_list = GalleryImage.objects.all().order_by('-uploaded_at')
    founders_list = TeamMember.objects.filter(member_type='founder').order_by('order', 'id')
    team_list = TeamMember.objects.filter(member_type='team').order_by('order', 'id')
    toppers_list = TopperResult.objects.all().order_by('order', 'id')
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
    total_toppers = toppers_list.count()
    total_admins = admins.count()
    total_certificates = certificates_list.count()
    total_broadcasts = broadcast_emails.count()
    # Build safe student broadcast JSON
    students_broadcast_data = []
    for s in students:
        if s.user and not s.user.is_staff and s.user.email and s.user.email.strip():
            name_val = f"{s.user.first_name} {s.user.last_name}".strip()
            if not name_val:
                name_val = s.user.username
            students_broadcast_data.append({
                "name": name_val,
                "username": s.user.username,
                "email": s.user.email.strip(),
                "course": s.course or ""
            })
    students_broadcast_json = json.dumps(students_broadcast_data)

    return render(request, 'admin_dashboard.html', {
        "students": students,
        "students_broadcast_json": students_broadcast_json,
        "admissions": admissions,
        "contacts": contacts,
        "courses": courses_list,
        "gallery_images": images_list,
        "founders": founders_list,
        "team_members": team_list,
        "toppers": toppers_list,
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
            "total_toppers": total_toppers,
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


@login_required(login_url='login')
def admin_export_students_excel(request):
    if not request.user.is_staff:
        return HttpResponse("Access denied", status=403)
        
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="TeachMantra_Registered_Students.csv"'
    
    # Write UTF-8 BOM for Microsoft Excel compatibility
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'S.No', 'Username', 'Full Name', 'Email Address', 'Phone Number', 
        'Registered Course', 'All India Rank', 'Grade', 'Account Status', 'Date Joined'
    ])
    
    students = StudentProfile.objects.select_related('user').all().order_by('-created_at')
    for idx, s in enumerate(students, 1):
        if not s.user.is_staff:
            full_name = f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username
            status = "Active" if s.user.is_active else "Inactive"
            date_joined = s.user.date_joined.strftime('%d-%m-%Y %H:%M') if s.user.date_joined else "N/A"
            writer.writerow([
                idx,
                s.user.username,
                full_name,
                s.user.email,
                s.phone,
                s.course,
                s.rank or "N/A",
                s.grade or "N/A",
                status,
                date_joined
            ])
            
    return response


@login_required(login_url='login')
def admin_export_admissions_excel(request):
    if not request.user.is_staff:
        return HttpResponse("Access denied", status=403)
        
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="TeachMantra_Admissions_Requests.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'S.No', 'Applicant Name', 'Email Address', 'Phone Number', 
        'Selected Course & Fee', 'Message / Query', 'Date Applied'
    ])
    
    admissions = Admission.objects.all().order_by('-created_at')
    for idx, adm in enumerate(admissions, 1):
        date_applied = adm.created_at.strftime('%d-%m-%Y %H:%M') if adm.created_at else "N/A"
        writer.writerow([
            idx,
            adm.name,
            adm.email,
            adm.phone,
            adm.course,
            adm.message or "",
            date_applied
        ])
        
    return response


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
def admin_update_course_view(request, course_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        duration = request.POST.get("duration", "").strip()
        fee = request.POST.get("fee", "").strip()
        description = request.POST.get("description", "").strip()
        image = request.FILES.get("image")

        if not title or not duration or not fee or not description:
            return JsonResponse({"status": "error", "message": "Please fill all required fields."})

        try:
            fee_val = int(fee)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Fee must be a valid number."})

        try:
            course = Course.objects.get(id=course_id)
            course.title = title
            course.duration = duration
            course.fee = fee_val
            course.description = description
            if image:
                course.image = image
            course.save()
            return JsonResponse({
                "status": "success", 
                "message": "Course updated successfully!",
                "course_id": course.id,
                "title": course.title,
                "duration": course.duration,
                "fee": course.fee,
                "description": course.description,
                "image_url": course.image.url if course.image else None
            })
        except Course.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Course not found."})
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


# ==========================================
# ACADEMIC MILESTONES & TOPPERS RESULTS VIEWS
# ==========================================
@csrf_exempt
@login_required(login_url='login')
def admin_add_result_view(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        exam_name = request.POST.get("exam_name", "").strip()
        rank = request.POST.get("rank", "").strip()
        badge = request.POST.get("badge", "").strip()
        order = request.POST.get("order", "0").strip()
        image = request.FILES.get("image")

        if not name or not exam_name:
            return JsonResponse({"status": "error", "message": "Student Full Name and Exam / Course name are required."})

        try:
            order_val = int(order) if order.isdigit() else 0
        except ValueError:
            order_val = 0

        try:
            topper = TopperResult.objects.create(
                name=name,
                exam_name=exam_name,
                rank=rank,
                badge=badge,
                order=order_val,
                image=image
            )
            return JsonResponse({
                "status": "success",
                "message": f"Topper '{name}' added successfully!",
                "topper_id": topper.id
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_update_result_view(request, result_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    try:
        topper = TopperResult.objects.get(id=result_id)
    except TopperResult.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Topper record not found."})

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        exam_name = request.POST.get("exam_name", "").strip()
        rank = request.POST.get("rank", "").strip()
        badge = request.POST.get("badge", "").strip()
        order = request.POST.get("order", "").strip()

        if not name or not exam_name:
            return JsonResponse({"status": "error", "message": "Student Full Name and Exam / Course name are required."})

        topper.name = name
        topper.exam_name = exam_name
        topper.rank = rank
        topper.badge = badge
        if order != "":
            try:
                topper.order = int(order)
            except ValueError:
                pass

        if 'image' in request.FILES and request.FILES['image']:
            topper.image = request.FILES['image']

        topper.save()

        return JsonResponse({
            "status": "success",
            "message": f"Details for topper '{topper.name}' updated successfully!",
            "topper_id": topper.id,
            "name": topper.name,
            "exam_name": topper.exam_name,
            "rank": topper.rank,
            "badge": topper.badge,
            "image_url": topper.image.url if topper.image else None
        })

    return JsonResponse({"status": "error", "message": "Invalid method."})


@csrf_exempt
@login_required(login_url='login')
def admin_delete_result_view(request, result_id):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        try:
            topper = TopperResult.objects.get(id=result_id)
            name = topper.name
            topper.delete()
            return JsonResponse({"status": "success", "message": f"Topper '{name}' deleted successfully!"})
        except TopperResult.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Topper record not found."})

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
            students_qs = students_qs.filter(Q(course__icontains=audience) | Q(course__iexact=audience))

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
        site_email = site_settings.contact_email if site_settings else "theteachmantra@gmail.com"
        site_phone = site_settings.contact_phone if site_settings else "+91 98765 43210"
        site_address = site_settings.contact_address if site_settings else "Academy Campus, Delhi, India"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f"{site_name} <theteachmantra@gmail.com>")

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
    
    attempted_test_map = {}
    if request.user.is_authenticated:
        user_fullname = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        submissions = TestSubmission.objects.filter(
            models.Q(user=request.user) |
            models.Q(student_email=request.user.email) |
            models.Q(student_name__iexact=user_fullname)
        )
        attempted_test_map = {s.test_id: s for s in submissions}

    return render(request, 'tests_list.html', {
        "tests": tests,
        "attempted_test_map": attempted_test_map
    })


@login_required(login_url='login')
def take_test_view(request, test_id):
    """
    Interactive test/quiz page matching the modern exam interface.
    Requires student authentication. Strictly enforces 1-attempt rule.
    """
    populate_default_online_tests()
    test = get_object_or_404(OnlineTest, id=test_id)
    
    # If test has an external link and user opted for redirect
    if test.external_link and request.GET.get('launch_external') == '1':
        return redirect(test.external_link)

    questions = test.questions.all().order_by('order', 'id')
    user_fullname = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    
    # Check if student has already submitted this test
    existing_sub = TestSubmission.objects.filter(
        models.Q(user=request.user, test=test) |
        models.Q(student_email=request.user.email, test=test) |
        models.Q(student_name__iexact=user_fullname, test=test)
    ).order_by('-submitted_at').first()
    
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

    review_list = []
    review_unlocked = False
    unlock_date_text = ""

    if existing_sub:
        sub_date = timezone.localtime(existing_sub.submitted_at).date() if existing_sub.submitted_at else timezone.now().date()
        today_date = timezone.localtime(timezone.now()).date()

        # Solutions & Answer Review unlocks on the next day onwards, or immediately for staff/admin
        if today_date > sub_date or request.user.is_staff:
            review_unlocked = True
            saved_ans = {}
            try:
                saved_ans = json.loads(existing_sub.answers_json) if existing_sub.answers_json else {}
            except Exception:
                saved_ans = {}
                
            for idx, q in enumerate(questions, start=1):
                ans = saved_ans.get(str(q.id)) or saved_ans.get(q.id) or None
                is_correct = (ans == q.correct_option)
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
        else:
            review_unlocked = False
            unlock_date = sub_date + timedelta(days=1)
            unlock_date_text = unlock_date.strftime("%d %b, %Y (Next Day / कल)")

    return render(request, 'quiz.html', {
        "test": test,
        "questions_count": questions.count(),
        "questions_json": json.dumps(questions_list, ensure_ascii=False),
        "already_attempted": bool(existing_sub),
        "existing_sub": existing_sub,
        "review_unlocked": review_unlocked,
        "unlock_date_text": unlock_date_text,
        "existing_review_json": json.dumps(review_list, ensure_ascii=False) if (review_unlocked and review_list) else "[]"
    })


@csrf_exempt
@login_required(login_url='login')
def submit_test_view(request, test_id):
    """
    Processes quiz answers submitted via AJAX, evaluates score, records submission,
    and returns scorecard. Solutions & answers review unlocks the next day.
    Enforces 1-attempt per student per test.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method."})

    test = get_object_or_404(OnlineTest, id=test_id)
    user_fullname = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    
    # Strictly block duplicate attempts
    existing_sub = TestSubmission.objects.filter(
        models.Q(user=request.user, test=test) |
        models.Q(student_email=request.user.email, test=test) |
        models.Q(student_name__iexact=user_fullname, test=test)
    ).first()
    
    if existing_sub:
        sub_date = timezone.localtime(existing_sub.submitted_at).date() if existing_sub.submitted_at else timezone.now().date()
        today_date = timezone.localtime(timezone.now()).date()
        review_unlocked = (today_date > sub_date) or request.user.is_staff
        unlock_date = sub_date + timedelta(days=1)

        return JsonResponse({
            "status": "already_attempted",
            "message": "Aap ye test pehle hi de chuke hain! Ek student sirf ek baar hi test attempt kar sakta hai.",
            "score": existing_sub.score,
            "wrong_count": existing_sub.wrong_count,
            "unanswered_count": existing_sub.unanswered_count,
            "total_questions": existing_sub.total_questions,
            "percentage": existing_sub.percentage,
            "passed": existing_sub.passed,
            "review_unlocked": review_unlocked,
            "unlock_date_text": unlock_date.strftime("%d %b, %Y (कल / Next Day)")
        })
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    student_name = user_fullname
    student_email = request.user.email or f"{request.user.username}@techmantra.com"
    user_answers = data.get("answers", {})  # e.g. {"1": "A", "2": "C"}

    questions = test.questions.all().order_by('order', 'id')
    total_q = questions.count()
    if total_q == 0:
        return JsonResponse({"status": "error", "message": "No questions available in this test."})

    score = 0
    wrong_count = 0
    unanswered_count = 0
    review_list = []

    for idx, q in enumerate(questions, start=1):
        ans = user_answers.get(str(q.id)) or user_answers.get(q.id) or None
        if ans is None or ans == "":
            unanswered_count += 1
            is_correct = False
        elif ans == q.correct_option:
            score += 1
            is_correct = True
        else:
            wrong_count += 1
            is_correct = False
            
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
        wrong_count=wrong_count,
        unanswered_count=unanswered_count,
        total_questions=total_q,
        percentage=percentage,
        passed=passed,
        answers_json=json.dumps(user_answers)
    )

    # On submission day, solutions review remains locked for students (unlocks next day)
    review_unlocked = bool(request.user.is_staff)
    tomorrow_date = timezone.localtime(timezone.now()).date() + timedelta(days=1)
    unlock_date_text = tomorrow_date.strftime("%d %b, %Y (कल / Next Day)")

    return JsonResponse({
        "status": "success",
        "student_name": student_name,
        "score": score,
        "wrong_count": wrong_count,
        "unanswered_count": unanswered_count,
        "total_questions": total_q,
        "percentage": percentage,
        "passed": passed,
        "pass_percentage": test.pass_percentage,
        "review_unlocked": review_unlocked,
        "unlock_date_text": unlock_date_text,
        "review": review_list if review_unlocked else []
    })


@login_required(login_url='login')
def admin_add_test_view(request):
    """
    Creates a new Online Test from Admin Dashboard.
    Supports auto-import from uploaded HTML Quiz file or pasted questions code.
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Access denied."})

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip() or "Mixed General Studies"
        subtitle = request.POST.get("subtitle", "").strip()
        description = request.POST.get("description", "").strip()
        
        parsed_questions = []
        
        # 1. Check if an HTML quiz file was uploaded
        if 'quiz_file' in request.FILES:
            file_obj = request.FILES['quiz_file']
            try:
                file_content = file_obj.read().decode('utf-8', errors='ignore')
                f_title, f_cat, f_questions = parse_quiz_html(file_content)
                if f_questions:
                    parsed_questions = f_questions
                if f_title and not title:
                    title = f_title
                if f_cat and category == "Mixed General Studies":
                    category = f_cat
            except Exception:
                pass
                
        # 2. Check if raw HTML or questions code was pasted
        raw_code = request.POST.get("raw_quiz_code", "").strip()
        if raw_code and not parsed_questions:
            try:
                f_title, f_cat, f_questions = parse_quiz_html(raw_code)
                if f_questions:
                    parsed_questions = f_questions
                if f_title and not title:
                    title = f_title
                if f_cat and category == "Mixed General Studies":
                    category = f_cat
            except Exception:
                pass

        if not title:
            title = "TeachMANTRA Practice Mock Test"

        try:
            duration_minutes = int(request.POST.get("duration_minutes") or 30)
        except (ValueError, TypeError):
            duration_minutes = 30
            
        total_q_count = len(parsed_questions) if parsed_questions else int(request.POST.get("total_questions") or 50)
            
        try:
            pass_percentage = int(request.POST.get("pass_percentage") or 40)
        except (ValueError, TypeError):
            pass_percentage = 40
            
        external_link = request.POST.get("external_link", "").strip()
        is_active = request.POST.get("is_active") in ["on", "true", "1", True]
        
        if not subtitle:
            subtitle = f"{total_q_count} Questions • {category} • परीक्षा अभ्यास"

        test = OnlineTest.objects.create(
            title=title,
            category=category,
            subtitle=subtitle,
            description=description or "Practice online mock tests designed by TeachMANTRA expert faculty.",
            duration_minutes=duration_minutes,
            total_questions=total_q_count,
            pass_percentage=pass_percentage,
            external_link=external_link,
            is_active=is_active
        )
        
        # Attach all parsed MCQs to the test
        for q in parsed_questions:
            QuizQuestion.objects.create(test=test, **q)

        msg = f"Test '{test.title}' created successfully!"
        if parsed_questions:
            msg = f"Test '{test.title}' with {len(parsed_questions)} MCQs imported and created successfully!"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({
                "status": "success",
                "message": msg,
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

