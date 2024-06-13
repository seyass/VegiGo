
# middleware.py
from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from authentication.models import vgUser

class CheckUserActiveMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated or 'username' in request.session:
            try:

                user = vgUser.objects.get(username=request.user.username)
            except:
                return None
            if user.is_blocked == True:
                if request.user.is_authenticated:
                    # For Django's authentication system
                    django_logout(request)
                if 'username' in request.session:
                    del request.session['username']
                    django_logout(request)    
                return render(request,'404.html')
        # Proceed to the next middleware or view
        return None


