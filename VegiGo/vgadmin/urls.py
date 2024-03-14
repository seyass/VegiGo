
from django.urls import path
from . import views


urlpatterns = [
    path('vgadmin/',views.admin_page,name='admin_page'),
    path('customers/',views.customers_page, name='customers'),
    path('dashboard/',views.dashboard_page,name='dashboard'),
    path('customrs/<int:user_id>/',views.update_page,name='customers')
    
    
]