from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    ### admin product management
    path('vgadmin/products/',views.products_page,name='products'),
    path('vgadmin/product/add',views.add_product,name='add_product'),
    path('vgadmin/product/update/<int:product_id>/', views.update_product, name='update_product'),
    path('vgadmin/product/edit/<int:product_id>/',views.edit_product,name='edit_product'),
    path('vgadmin/product/edit/<int:product_id>/delete-secondary/<int:secondary_image_id>/', views.delete_secondary_image, name='delete_secondary_image'),
    path('vgadmin/product/delete/<int:product_id>/',views.update_product,name='delete_product'),

    ### admin category management
    path('vgadmin/categories/',views.category_page,name='categories'),
    path('vgadmin/category/add',views.create_category,name='create_category'),
    path('vgadmin/category/edit/<int:catId>/',views.edit_category,name='edit_category'),
    path('vgadmin/category/delete/<int:catId>/',views.delete_category,name='deleteCategory'),
    path('vgadmin/category/update/<int:category_id>/', views.update_category, name='update_category'),
    
    ### admin offer management
    path('vgadmin/offer',views.offer_page,name='offer_page'),
    path('vgadmin/category/offer/add/',views.add_category_offer,name='add_category_offer'),
    path('vgadmin/category/offer/edit/<int:offerId>/',views.edit_category_offer,name='edit_category_offer'),
    path('vgadmin/category/offer/delete/<int:offerId>',views.delete_category_offer,name='delete_category_offer'),
    path('vgadmin/product/offer/add/',views.add_product_offer,name='add_product_offer'),
    path('vgadmin/product/offer/edit/<int:offerId>/',views.edit_product_offer,name='edit_product_offer'),
    path('vgadmin/product/offer/delete/<int:offerId>',views.delete_product_offer,name='delete_product_offer'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)