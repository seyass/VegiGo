from django.urls import path
from . import views


urlpatterns = [
    # profile
    path('user/profile/<int:userId>/',views.user_profile,name='user_profile'),
    path('user/profile/edit/<int:userId>/',views.edit_profile,name='edit_profile'),
    path('user/profile/edit/password/<int:userId>/',views.edit_password,name='edit_password'),

    # user cart
    path('cart/',views.cart_page,name='cart_page'),
    path('cart/add/<int:productId>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/update/',views.update_cart_item, name='update_cart_item'),
    path('cart/update/location/',views.update_cart_location,name='update_cart_location'),

    # user address
    path('profile/address/<int:userId>/',views.address_page,name="address_page"),
    path('profile/address/edit/<int:addressId>/',views.edit_address,name='edit_address'),
    path('profile/address/delete/<int:addressId>/',views.delete_address,name='delete_address'),

    # checkout and coupon
    path('checkout/<int:cartId>/',views.checkout_page,name='checkout_page'),
    path('checkout/coupon/apply/',views.apply_coupon,name='apply_coupon'),
    path('checkout/coupon/remove/',views.remove_coupon,name='remove_coupon'),

    # user order
    path('orders/',views.orders_page,name='orders_page'),
    path('order/detail/<int:orderId>/',views.order_detail,name='order_detail'),
    

    # wallet
    path('wallet/',views.wallet_page,name='wallet_page'),

    #wishlist
    path('wishlist/',views.wishlist_page,name='wishlist_page'),
    path('wishlist/add/<int:productId>/',views.add_wishlist,name='add_wishlist'),
    path('wishlist/delete/<int:productId>/',views.delete_wishlist,name='delete_wishlist'),
    path('wishlist/cart/add/<int:productId>/',views.add_to_cart_wishlist,name='add_to_cart_wishlist'),

  
    
]