
from django.urls import path,include
from . import views



urlpatterns = [
    ## User
    # order and details
    path('placeorder/',views.place_order,name='place_order'),
    path('order/payment/<int:orderId>/',views.failed_payment,name='failed_payment'),
    path('user/order/cancel/<int:orderItemId>/',views.user_order_cancel,name='user_order_cancel'),
    path('order/<int:orderId>/invoice',views.download_invoice,name='download_invoice'),
    path('order_success/',views.order_success,name='order_success'),

    # review and ratings
    path('user_review/<int:orderItemId>/',views.user_review,name='user_review'),

    # return and request
    path('order/detail/return/request/<int:itemId>/',views.return_request,name='return_request'),

    ## Admin
    
    path('vgadmin/orders/',views.admin_orders,name='admin_orders'),
    path('vgadmin/order/detail/<int:orderId>/',views.admin_order_detail,name='admin_order_detail'),
    path('vgadmin/order/status/update/',views.update_order_status,name='update_order_status'),
    path('razorpay/payment/verification', views.verify_payment, name='verify_payment'),

]