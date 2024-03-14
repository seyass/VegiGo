from django.urls import path,include
from . import views

urlpatterns = [
    path('signup_page/',views.signup_page,name='signup_page'),
    path('signin_page/',views.signin_page,name='signin_page'),
    path('logout_page',views.logout_page,name='logout_page'),
    path('otp_verification/',views.otp_verification,name="otp_verification"),
    path('homepage',views.home_page, name='home_Page'),
]