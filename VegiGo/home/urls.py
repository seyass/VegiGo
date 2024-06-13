from django.urls import path
from . import views


urlpatterns = [
    # homepage
    path('',views.home_page,name='home_page'),

    # product page
    path('shop/',views.shop_page,name="shop_page"),
    path('shop/product/<int:proId>/',views.product_shop_page,name= "product_shop_page"),
    path('shop/category/<int:catId>/',views.category_select,name='category_select'),
    path('shop/filter/<int:sort_by>',views.filter_product_list,name='filter_product_list'),
    path('shop/search/product',views.search_product,name='search_product')
]