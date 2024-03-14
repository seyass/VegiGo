from django.shortcuts import render,redirect
from authentication.models import vgUser


def admin_page(request):
    


    return render(request, "base.html")
# Create your views here.

def customers_page(request):

    customers = vgUser.objects.all()
    
    
        
    

    return render(request, 'customers.html',{"customers":customers})



def dashboard_page(request):
    

    return render(request, 'home/index.html')



def update_page(request,user_id):
    user=vgUser.objects.get(pk=user_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'active':
            user.is_blocked = False
        elif new_status == 'blocked':
            user.is_blocked = True
        user.save()
        return redirect(customers_page)
        


    return redirect(customers_page)