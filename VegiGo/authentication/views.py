
from django.urls import reverse_lazy
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from allauth.socialaccount.models import SocialAccount
from productmanagement.models import Category
from customer.models import Cart,CartItem,Wallet
from .models import vgUser
import datetime
import random


bg_image_url = settings.STATIC_URL + 'images/Gemini_Generated_Image.jpeg'

def google_authenticate(request):

    try:
        social_account = SocialAccount.objects.get(provider='google', user=request.user)
        customer = social_account.user
        users = vgUser.objects.filter(is_blocked=False).all()
        if customer not in users:
            msg = 'This account has been blocked'
            return render(request,'authentication/signin.html',{'msg':msg,'background': bg_image_url})
        try:
            wallet = Wallet.objects.get(user=customer)
        except:
            wallet = Wallet.objects.create(user=customer)
        # Log the customer in and create session
        login(request, customer, backend='django.contrib.auth.backends.ModelBackend')
        customer.is_google = True
        customer.save()
        return redirect(home_page)  # Redirect to home page upon successful login
    
    except SocialAccount.DoesNotExist:
        # Handle case when social account is not found
        return redirect(signin_page)

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
        otp_sent_time_str = request.session.get('otp_sent_time', '')

        if otp_sent_time_str:
            # Convert 'otp_sent_time' from string to a timezone-aware datetime
            otp_sent_time = datetime.datetime.strptime(otp_sent_time_str, '%Y-%m-%d %H:%M:%S')
            otp_sent_time = timezone.make_aware(otp_sent_time, timezone.get_current_timezone())
        else:
            otp_sent_time = None

        # Calculate the time difference and check if the OTP is valid and not expired
        time_difference  = 0
        if entered_otp == stored_otp and otp_sent_time:
            time_difference = (timezone.now() - otp_sent_time).total_seconds()
        # Check if OTP is valid and not expired
        if time_difference < 30:
            username = request.session.get('username')
            email = request.session.get('email')
            password = request.session.get('password')
            customer = vgUser.objects.create_user(username=username, email=email, password=password)
            wallet = Wallet.objects.create(user=customer,amount=0)

            del request.session['otp']
            del request.session['otp_sent_time']
            del request.session['username']
            del request.session['email']
            del request.session['password']
            return render(request,'authentication/user_success.html') 
        else:
            error_message = 'The incorrect otp'
            return render(request,'authentication/otp_verification.html',{'error_message':error_message}) 

    else:
        return render(request, "authentication/otp_verification.html")

def resend_otp(request):
    
    # Check if previous OTP is expired
    otp_sent_time_str = request.session.get('otp_sent_time', None)
    otp_sent_time = None

    if otp_sent_time_str:
        # Convert the string time to a naive datetime object
        otp_sent_time_naive = datetime.datetime.strptime(otp_sent_time_str, '%Y-%m-%d %H:%M:%S')
        # Convert the naive datetime to timezone-aware datetime
        otp_sent_time = timezone.make_aware(otp_sent_time_naive, timezone.get_current_timezone())

    # Calculate the time difference
    time_difference = 0
    if otp_sent_time:
        time_difference = (timezone.now() - otp_sent_time).total_seconds()
        
        # Check if the time difference is greater than 30 seconds
    if time_difference > 30:
        
        # Generate OTP only if the previous OTP is expired
        otp = random.randint(100000, 999999)
        # Save OTP in session
        request.session['otp'] = str(otp)
        # Save current time in session
        request.session['otp_sent_time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        # Send OTP via email
        email = request.session.get('email')
        subject = 'Resend OTP for Signup'
        message = f'Your new OTP for signup is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        send_mail(subject, message, from_email, to_email)
        return redirect('otp_verification')
    else:
        error_message = 'The otp verification failed'
        return render(request,'authentication/otp_verification.html',{'error_message':error_message})

def signup_page(request):
    bg_image_url = settings.STATIC_URL + 'images/Gemini_Generated_Image.jpeg'
    usernames = vgUser.objects.values_list('username', flat=True)
    emails = vgUser.objects.values_list('email', flat=True)
    if 'username' in request.session:
        return redirect(home_page)
    elif 'isusername' in request.session:
        return render(request, 'admin/VgAdmin.html')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_check = password.strip()
            if len(password_check)<6:
                error_message = 'Password need minimum 6 character'
                return render(request,'authentication/signup.html',{'error_message':error_message,'background': bg_image_url})
            trimmed_username = username.strip()
            trimmed_email = email.lower().strip()
            
            if not (username or email or password):
                error_message = "All fields are required."
                return render(request, 'authentication/signup.html', {'error_message': error_message, 'background': bg_image_url})
            if username in usernames or email in emails:
                error_message = "User already exists"
                return render(request, 'authentication/signup.html', {"error_message": error_message, 'background': bg_image_url})
            if not trimmed_username:
                error_message = "Username field required"
                return render(request, "authentication/signup.html", {"error_message": error_message, "background": bg_image_url})
            if not trimmed_email:
                error_message = "Email field required"
                return render(request, 'authentication/signup.html', {"error_message": error_message, 'background': bg_image_url})

            # Generate OTP
            otp = random.randint(100000, 999999)
            # Save OTP in session
            request.session['otp'] = str(otp)
            # Save current time in session
            request.session['otp_sent_time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
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
    return render(request, 'authentication/signup.html', {'background': bg_image_url})

def signin_page(request):

    # Check if customer is already logged in
    if request.user.is_authenticated:
        return redirect('home_page')
        
        return redirect(home_page)
    elif 'isusername' in request.session:
        return render(request, 'admin/VgAdmin.html')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        customer = authenticate(username=username, password=password)
        ai = vgUser.objects.filter(is_blocked=False).all()
        
        if customer is not None:
            if customer.is_superuser:
                login(request, customer)
                request.session['isusername'] = username
                return render(request, 'admin/VgAdmin.html')
            else:
                if customer in ai:
                    print('vannu')
                    request.session['username'] = username
                    categories = Category.objects.all().order_by('name')
                    login(request, customer)
                    
                    return render(request, 'home/index.html', {'categories': categories,'customer':customer})
                else:
                    msg = 'This account has been blocked'
                    return render(request,'authentication/signin.html',{'msg':msg,'background': bg_image_url})
        else:
            msg = 'Incorrect username or password'
            return render(request,'authentication/signin.html',{'msg':msg,'background': bg_image_url})
    
    return render(request, 'authentication/signin.html', {'background': bg_image_url})

@never_cache
def logout_page(request):

    if request.user.is_authenticated:
        # For Django's authentication system
        if 'username' in request.session:
            del request.session['username']
            logout(request)
        if 'isusername' in request.session:
            del request.session['isusername']
            logout(request)
        logout(request)
        return redirect(home_page)

    if 'username' in request.session:
        del request.session['username']
        logout(request)
        return redirect(home_page)
    elif 'isusername' in request.session:
        del request.session['isusername']
        logout(request)
        return redirect(home_page)
    
    return redirect(signin_page)

def home_page(request):
    categories = Category.objects.filter(is_active=True).order_by('name')
    if request.session == 'username' or request.user.is_authenticated: 
        if request.session == 'username':
            customer = vgUser.objects.get(username=request.session['username']) 
            print(customer)
        elif request.user.is_authenticated:
            print('ivide anu')
            customer = vgUser.objects.get(username=request.user.username)
            print(customer.username)
        try:

            cart = Cart.objects.get(user=vgUser.objects.get(username=customer))
            items = CartItem.objects.filter(cart=cart)
            print(categories)
        except:
            cart = None
            items = []
        
        return render(request,'home/index.html',{'categories':categories,'customer':customer,'items':items})
    elif 'isusername' in request.session:
        
        return render(request,'admin/VgAdmin.html')
    

    return render(request,'home/index.html',{'categories':categories,})

def forgot_password(request):

    msg = None
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = vgUser.objects.get(email=email)
            
        except:
               msg = 'Email not found'
               return render(request, 'authentication/forgot_password.html',{'msg':msg,'background': bg_image_url})
                


    return render(request, 'authentication/forgot_password.html',{'msg':msg,'background': bg_image_url})

