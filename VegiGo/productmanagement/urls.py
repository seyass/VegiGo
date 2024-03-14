from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('products/',views.products_page,name='products'),
    path('categories/',views.category_page,name='categories'),
    path('add_product/',views.add_product,name='add_product'),
    path('create_category/',views.create_category,name='create_category'),
    path('edit_category/<int:catId>/',views.edit_category,name='edit_category'),
    path('deleteCategory/<int:catId>/',views.delete_category,name='deleteCategory')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)