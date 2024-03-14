from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
import random
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from productmanagement.models import Category
from .models import vgUser

# Signup page
def signup_page(request):
    if 'username' in request.session:
        return render(request, 'index.html')
    elif 'isusername' in request.session:
        return render(request, 'index.html')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            if not (username and email and password):
                error_message = "All fields are required."
                return render(request, 'signup.html', {'error_message': error_message})

            # Generate OTP
            otp = random.randint(100000, 999999)
            # Save OTP in session

            request.session['otp'] = str(otp)
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password

            # Send OTP via email
            subject = 'OTP for Signup'
            message = f'Your OTP for signup is: {otp}'
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]
            send_mail(subject, message, from_email, to_email)

            return redirect('otp_verification')

    bg_image_url = settings.STATIC_URL + 'images/Gemini_Generated_Image.jpeg'
    return render(request, 'signup.html', {'background': bg_image_url})

# Sign in page
def signin_page(request):
    bg_image_url = settings.STATIC_URL + 'images/Gemini_Generated_Image.jpeg'
    msg = None
    if 'username' in  request.session:
        return redirect(home_page)
    elif 'isusername' in request.session:
        return redirect(home_page)    
    
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        ai = vgUser.objects.all()
        if user is not None:
            if user.is_superuser:
                login(request,user)
                request.session['isusername']=username
                return redirect(home_page)
            else:
                
                login(request,user)
                request.session['username']=username
                return redirect(home_page)
        else:
            msg = "Incorrect password or username"
            return render(request,'signin.html',{'msg':msg ,'background': bg_image_url})
    
    return render(request, 'signin.html', {'background': bg_image_url})

    

def logout_page(reqest):

    
    return redirect('signin_page')

def admin_page(request):
    return render(request, 'VgAdmin.html')

# OTP verification page

def otp_verification(request):
    if request.method == 'POST':
        # Get the entered OTP digits from the form
        otp_digits = [
            request.POST.get('otp1', ''),
            request.POST.get('otp2', ''),
            request.POST.get('otp3', ''),
            request.POST.get('otp4', ''),
            request.POST.get('otp5', ''),
            request.POST.get('otp6', ''),
        ]
        entered_otp = ''.join(otp_digits)
        stored_otp = request.session.get('otp', '')

        if entered_otp == stored_otp:
            username = request.session.get('username')
            email = request.session.get('email')
            password = request.session.get('password')
            user = vgUser.objects.create_user(username=username,email=email,password=password)
            
            del request.session['otp']
            
            return redirect('signin_page') 

        else:
            
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('otp_verification') 

    else:
        
        return render(request, "otp_verification.html")
      
def home_page(request):
    
    categories = Category.objects.all()
    print(categories)
    print('hello')

    return render(request,'index.html',{'categories':categories})