
from django.shortcuts import render, redirect
from .models import Category,Product,SecondaryImage


def create_category(request):
    create_mode = True
    edit_mode = False
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_file = request.FILES['image']
        
        new_category = Category(name=name, description=description)
        new_category.image = image_file
        new_category.save()
        
        return redirect(category_page)  # Replace 'category_page' with the appropriate URL name
    
    return render(request, 'create_category.html', {'create_mode': create_mode, 'edit_mode': edit_mode})



def add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        print('ethi')
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        selling_price = request.POST['selling_price']
        quantity = request.POST['quantity']
        primary_image = request.FILES['primary_image']
        discount = (float(price)-float(selling_price))/float(price)*100

        # Create the product
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            selling_price=selling_price,
            quantity=quantity,
            primary_image=primary_image,
            discount=discount
        )

        # Handle secondary images
        secondary_images = request.FILES.getlist('secondary_images')
        for image in secondary_images:
            SecondaryImage.objects.create(product=product, image=image)

        return redirect(products_page) 

    return render(request, 'addproduct.html',{'categories':categories})


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
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def edit_product(proId):
    
    return redirect(products_page)