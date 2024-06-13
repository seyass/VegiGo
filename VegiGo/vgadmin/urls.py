
from django.urls import path
from . import views


urlpatterns = [
    # admin
    path('vgadmin/',views.admin_page,name='admin_page'),

    #custoemrs
    path('customers/',views.customers_page, name='customers'),
    path('customrs/<int:user_id>/',views.update_page,name='customers'),

    # dashboard
    path('dashboard/',views.dashboard_page,name='dashboard'),
    path('report/',views.admin_report,name='admin_report'),
    path('dashboard/data/', views.get_dashboard_data, name='get_sales_data'),

    # branches 
    path('branches/',views.branches_page,name='branches_page'),
    path('branch/edit/<int:branchId>/',views.edit_branch,name='edit_branch'),
    path('branch/delete/<int:branchId>/',views.delete_branch,name='delete_branch'),
    
    # coupon urls
    path('coupon/',views.coupon_page,name='coupon_page'),
    path('coupon/add',views.add_coupon,name='add_coupon'),
    path('coupon/edit/<int:couponId>/',views.edit_coupon,name='edit_coupon'),
    path('coupon/delete/<int:couponId>/',views.delete_coupon,name='delete_coupon'),
    
    
]