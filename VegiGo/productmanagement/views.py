
from django.shortcuts import render, redirect
from .models import Category
from PIL import Image
from io import BytesIO

# code for croping the image
def crop_image(image_file, crop_x, crop_y, crop_width, crop_height):
    image = Image.open(image_file)
    cropped_image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
    if cropped_image.mode != 'RGB':
        cropped_image = cropped_image.convert('RGB')
    cropped_image_io = BytesIO()
    cropped_image.save(cropped_image_io, format='JPEG')
    return cropped_image_io.getvalue()


def create_category(request):
    create_mode = True
    edit_mode = False
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        crop_x = float(request.POST.get('crop_x'))
        crop_y = float(request.POST.get('crop_y'))
        crop_width = float(request.POST.get('crop_width'))
        crop_height = float(request.POST.get('crop_height'))
        image_file = request.FILES['image']
        
        cropped_image_data = crop_image(image_file, crop_x, crop_y, crop_width, crop_height)
        
        new_category = Category(name=name, description=description)
        new_category.image.save(image_file.name, BytesIO(cropped_image_data), save=False)
        new_category.save()
        
        return redirect(category_page) 
    
    return render(request, 'create_category.html', {'create_mode': create_mode, 'edit_mode': edit_mode})

def add_product(request):



    return render(request,'addproduct.html')

# Create your views here.
def edit_category(request,catId):
    edit_mode = True
    create_mode = False
    category = Category.objects.get(pk=catId)




    return render(request,'create_category.html',{'edit_mode':edit_mode,'create_mode':create_mode,'category':category})

def delete_category(request,catId):
    category = Category.objects.get(pk = catId)
    category.delete()
    return redirect(category_page)

def category_page(request):
    # views.py

    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})



def products_page(request):

    return render(request,'products.html')