from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages  # Import for displaying messages
from .models import Category, Product, SecondaryImage,Location,ProductLocations,CategoryOffer,ProductOffer
from .forms import CategoryForm,ProductForm,ProductLocationForm,CategoryOfferForm,ProductOfferForm
import os
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from authentication.views import signin_page
from .forms import CategoryForm,ProductForm
from django.db import IntegrityError
from django.db.models import Sum
from vgadmin import models as vgadmin_models

def admin_page(request):
    if 'isusername' in request.session:
        return render(request, 'admin/base.html')
    else:
        
        return redirect(signin_page)

################ Category ################

def create_category(request):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect(signin_page)

    if request.method == 'POST':
        #try:
        name = request.POST.get('name')
        cleaned_name = name.strip()
        if len(cleaned_name) ==0:
            msg = 'All fields required'
            return JsonResponse({'message': msg}, status=400)
        description = request.POST.get('description')
        image_file = request.POST.get('cropped_image')
        new_category = Category(name=name, description=description)
        new_category.image = image_file
        new_category.save()
        
        return JsonResponse({'message': 'Category created successfully'})

        # except IntegrityError:
        #     # Handle integrity constraint violation error
        #     msg = 'The category already exists'
        #     return JsonResponse({'message': msg}, status=400)

    return render(request, 'admin/product/add_category.html')

def edit_category(request, catId):

    if 'isusername' not in request.session:
        
        return redirect(signin_page)
    edit_mode = True
    category = Category.objects.get(pk=catId)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect(category_page)
        else:
            return render(request,'admin/product/edit_category.html',{'form':form})
    else:
        form = CategoryForm(instance=category)
        
    return render(request, 'admin/product/edit_category.html', {'form': form, 'edit_mode': edit_mode})

def delete_category(request, catId):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        messages.error(request, "You need to sign in first.")
        return redirect(signin_page)

    category = Category.objects.get(pk=catId)
    category.delete()
    return redirect(category_page)

def category_page(request):

    if 'isusername' not in request.session:
        
        return redirect(signin_page)

    categories = Category.objects.all().order_by('name')
    return render(request, 'admin/product/categories.html', {'categories': categories})

def update_category(request, category_id):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect(signin_page)

    category = Category.objects.get(pk=category_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'active':
            category.is_active = True
        elif new_status == 'blocked':
            category.is_active = False
        category.save()
        return redirect(category_page)
    else:
        return redirect(category_page)

@receiver(pre_delete, sender=Category)
def delete_category_media(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

################ Product ################

def products_page(request):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        
        return redirect(signin_page)

    products = Product.objects.filter(is_active=True).annotate(total_quantity=Sum('productlocations__quantity'))
    return render(request, 'admin/product/products.html', {'products': products})

def add_product(request):
    
    if 'isusername' not in request.session:
        return redirect(signin_page)

    categories = Category.objects.all()
    locations = vgadmin_models.Branches.objects.all()
    if request.method == 'POST':
        productForm = ProductForm(request.POST, request.FILES)
        productLocationForm = ProductLocationForm(request.POST, request.FILES)
    
        if productForm.is_valid():
            try:
                category_id = productForm.cleaned_data['category']
                category = Category.objects.get(pk=category_id.id)
                price = productForm.cleaned_data['price']
                selling_price = productForm.cleaned_data['selling_price']
                discount = (float(price) - float(selling_price)) / float(price) * 100
                if price < 1:
                    productForm.add_error('selling_price','Enter a valid price')
                    return render(request, 'admin/product/add_product.html', {'productForm': productForm, 'categories': categories,'locations':locations,'form':productForm})
                if selling_price < 1:
                    productForm.add_error('selling_price','Enter a valid selling price')
                
                product = productForm.save(commit=False)
                product.category = category
                product.discount = discount
                product.save()
                
                for image in request.FILES.getlist('secondary_images'):
                    SecondaryImage.objects.create(product=product, image=image)

                # handle locations and quantity
                selected_locations = request.POST.getlist('locations')
                for location_id in selected_locations:
                    quantity = request.POST.get(f'quantity_{location_id}')
                    
                    if quantity:
                        quantity = int(quantity)

                        ProductLocations.objects.create(
                            product=product,
                            location=vgadmin_models.Branches.objects.get(id=location_id),
                            quantity=quantity
                        )
                return redirect(products_page)

                
            except IntegrityError:
                msg = "The product already exists"
                return render(request, 'admin/product/add_product.html', {'productForm': productForm, 'categories': categories,'msg':msg,'locations':locations})
        else:

            return render(request, 'admin/product/add_product.html', {'productForm':productForm,'productLocationForm':productLocationForm,'locations':locations,'categories':categories})
        
        
    
    else:
        productForm = ProductForm()
        productLocationForm = ProductLocationForm()
    return render(request, 'admin/product/add_product.html', {'productForm':productForm,'productLocationForm':productLocationForm,'locations':locations,'categories':categories})

def update_product(request, product_id):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect(signin_page)

    product = Product.objects.get(pk=product_id)
    product.is_active = False
    product.save()
    return redirect(products_page)
    

def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    locations = vgadmin_models.Branches.objects.all()
    product_locations = ProductLocations.objects.filter(product=product).values_list('location_id', flat=True)
    product_quantities = {pl.location_id: pl.quantity for pl in ProductLocations.objects.filter(product=product)}
    categories = Category.objects.all()
    secondary_images = None
    try:
        secondary_images = SecondaryImage.objects.filter(product=product)
    except:
        pass
    if request.method == 'POST':
        productForm = ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            price = productForm.cleaned_data['price']
            selling_price = productForm.cleaned_data['selling_price']
            if price < 1:
                productForm.add_error('selling_price','Enter a valid price')
                return render(request, 'admin/product/add_product.html', {'productForm': productForm, 'categories': categories,'locations':locations,'form':productForm,'product':product})
            if selling_price < 1:
                productForm.add_error('selling_price','Enter a valid selling price')
                return render(request, 'admin/product/add_product.html', {'productForm': productForm, 'categories': categories,'locations':locations,'form':productForm,'product':product})
            product = productForm.save()

            # Clear existing locations
            ProductLocations.objects.filter(product=product).delete()
            for image in request.FILES.getlist('secondary_images'):
                SecondaryImage.objects.create(product=product, image=image)
            # Add new locations and quantities
            for location in locations:
                if str(location.id) in request.POST.getlist('locations'):
                    quantity = request.POST.get(f'quantity_{location.id}')
                    if quantity:
                        ProductLocations.objects.create(product=product, location=location, quantity=int(quantity))
            for image in request.FILES.getlist('secondary_images'):
                    SecondaryImage.objects.create(product=product, image=image)
        else:
            context = {
                'productForm': productForm,
                'locations': locations,
                'product_locations': product_locations,
                'product_quantities': product_quantities,
                'product':product,
                'secondary_images':secondary_images
            }
            return render(request, 'admin/product/edit_product.html', context)
            
        return redirect('products')  # Assuming you have a product list view

    else:

        productForm = ProductForm(instance=product)

    context = {
        'secondary_images':secondary_images,
        'productForm': productForm,
        'locations': locations,
        'product_locations': product_locations,
        'product_quantities': product_quantities,
        'product':product,
    }
    return render(request, 'admin/product/edit_product.html', context)

def delete_secondary_image(request, product_id, secondary_image_id):
    if request.method == 'POST':
        # Get the product and the secondary image
        product = Product.objects.get(id=product_id)
        secondary_image = SecondaryImage.objects.get(id=secondary_image_id)

        # Check if the secondary image belongs to the product
        if secondary_image.product == product:
            # Delete the secondary image
            secondary_image.delete()

    # Redirect back to the edit product page
    return redirect('edit_product', product_id=product_id)

def delete_product(request, proId):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        messages.error(request, "You need to sign in first.")
        return redirect(signin_page)

    product = Product.objects.get(pk=proId)
    product.delete()
    return redirect(products_page)

@receiver(pre_delete, sender=Product)
def delete_product_media(sender, instance, **kwargs):
    # Delete associated media files
    if instance.primary_image:
        if os.path.isfile(instance.primary_image.path):
            os.remove(instance.primary_image.path)

    # Delete secondary images
    secondary_images = instance.secondaryimage_set.all()
    for secondary_image in secondary_images:
        if os.path.isfile(secondary_image.image.path):
            os.remove(secondary_image.image.path)

################ offer ################

def offer_page(request):

    categoryOffers = CategoryOffer.objects.all()
    productOffers = ProductOffer.objects.all()
    
    return render(request,'admin/offer/offer.html',{'categoryOffers':categoryOffers,'productOffers':productOffers})

def add_category_offer(request):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect('sigin_page')
    
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        
        if form.is_valid():
            
            form.save()        
            return redirect('offer_page')
        else:
            return render(request,'admin/offer/add_offer.html',{'form':form})
    else:
        form = CategoryOfferForm()
        return render(request,'admin/offer/add_offer.html',{'form':form})

def edit_category_offer(request,offerId):
    
    offer = CategoryOffer.objects.get(id=offerId)

    if request.method == 'POST':
        form = CategoryOfferForm(request.POST,instance=offer)
        if form.is_valid():

            form.save()
            return redirect('offer_page')
        else:
            return render(request,'admin/offer/edit_offer.html',{'form':form})
    else:
        form = CategoryOfferForm(instance=offer)
        return render(request,'admin/offer/edit_offer.html',{'form':form})

def delete_category_offer(request,offerId):

    offer = CategoryOffer.objects.get(id=offerId)
    
    offer.delete()
    return redirect('offer_page')
    
def add_product_offer(request):

    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect('sigin_page')
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offer_page')
        else:
            return render(request,'admin/offer/add_offer.html',{'form':form})
    else:
        form = ProductOfferForm()
        return render(request,'admin/offer/add_offer.html',{'form':form})

def edit_product_offer(request,offerId):
    
    offer = ProductOffer.objects.get(id=offerId)

    if request.method == 'POST':
        form = ProductOfferForm(request.POST,instance=offer)
        if form.is_valid():
            
            form.save()
            return redirect('offer_page')
        else:
            return render(request,'admin/offer/edit_offer.html',{'form':form})
    else:
        form = ProductOfferForm(instance=offer)
        return render(request,'admin/offer/edit_offer.html',{'form':form})

def delete_product_offer(request,offerId):

    offer = ProductOffer.objects.get(id=offerId)
    offer.delete()
    return redirect('offer_page')
    


