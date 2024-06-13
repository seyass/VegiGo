from django.urls import path,include
from . import views

urlpatterns = [
    path('signup_page/',views.signup_page,name='signup_page'),
    path('signin_page/',views.signin_page,name='signin_page'),
    path('logout_page',views.logout_page,name='logout_page'),
    path('otp_verification/',views.otp_verification,name="otp_verification"),
    path('google-authenticate/',views.google_authenticate, name='google_authenticate'),
    path('homepage/',views.home_page, name='home_Page'),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('forgot_password/',views.forgot_password,name='forgot_password')
    
]