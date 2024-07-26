from decimal import Decimal
from django.shortcuts import render
from productmanagement.models import Category,Product, Review
from django.db.models import Q,Avg
from authentication.models import vgUser
import json
from customer.models import Cart,CartItem
from productmanagement.models import Product, CategoryOffer, ProductOffer

from django.utils import timezone

def check_offer(productId):
    
    product = Product.objects.get(id=productId)
    product.special_discount = product.selling_price
    product.save()
    category = product.category
    product.max_discount = 0
    try:
        high_discount = 0
        categoryOffer = CategoryOffer.objects.filter(category=category)
        current_date = timezone.now().date()
        for offer in categoryOffer:
            if offer.start_date <= current_date <= offer.end_date:
                if offer.discount > high_discount:
                    high_discount = offer.discount
                    
        discount_amount = (high_discount / Decimal(100)) * product.selling_price
        discount_price = product.selling_price - discount_amount
        
        if product.special_discount > discount_price:
            product.special_discount = discount_price
            product.max_discount = high_discount
            product.save()
        else:
            product.max_discount = 0
            product.special_discount = product.selling_price
    
    except:
        pass
    try:
        productOffer = ProductOffer.objects.filter(product=product)
        for offer in productOffer:
            if offer.start_date <= current_date <= offer.end_date:
                if offer.discount > high_discount:
                    high_discount = offer.discount
        discount_amount = (high_discount / Decimal(100)) * product.selling_price
        discount_price = product.selling_price - discount_amount
        if product.special_discount >= discount_price:
            product.special_discount = discount_price
            product.max_discount = high_discount
            product.save()
        else:
            product.max_discount = 0
            product.special_discount = product.selling_price
    except:
        pass
    product.max_discount += product.discount
    print(product.special_discount)
    return product

# Create your views here.
def home_page(request):
    
    categories = Category.objects.filter(is_active=True).all().order_by('name')
    if request.session == 'username' or request.user.is_authenticated: 
        if request.session == 'username':
            customer = vgUser.objects.get(username=request.session['username']) 
        elif request.user.is_authenticated:
            customer = vgUser.objects.get(username=request.user.username)
        try:
            cart = Cart.objects.get(user=customer)
            items = CartItem.objects.filter(cart=cart)
        except:
            items = None
            pass
        return render(request, 'home/index.html',{'categories':categories,'items':items})
    categories = Category.objects.filter(is_active=True).all().order_by('name')
    return render (request, 'home/index.html',{'categories':categories})
        
def shop_page(request):

    customer = False
    products = Product.objects.filter(is_active = True).all()
    categories = Category.objects.filter(is_active=True).all()
    for product in products:
        check_offer(product.id)
    items = None
    productItems = []
    if 'username' in request.session or request.user.is_authenticated:
        customer = request.user
        try:
            cart = Cart.objects.get(user=customer)
            items = CartItem.objects.filter(cart=cart)
            for item in items:
                productItems.append(item.product)
        except:
            items = None
        context = {
            'products':products,
            'productItems':productItems,
            'customer':customer,
            'items':items,
            'categories':categories
        }
        return render(request, 'home/shop.html', context)
    

    return render(request, 'home/shop.html', {"products": products,'categories': categories,'customer': customer,'items':items})

def product_shop_page(request, proId):

    customer = False
    productItems = []
    try:
        product = Product.objects.get(pk=proId)
        reviews = Review.objects.filter(product=product).order_by('-id')[:4]
        rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        category_products = Product.objects.filter(category=product.category, is_active=True).exclude(pk=proId)[:6]
        customer = None
        
        product = check_offer(proId)
        
        if 'username' in request.session or request.user.is_authenticated:
            
            customer = request.user
            try:
                cart = Cart.objects.get(user=customer)
                items = CartItem.objects.filter(cart=cart)
                for item in items:
                    productItems.append(item.product)
                context = {
                    'product': product, 
                    'featured_products': category_products,
                    'reviews':reviews,'customer':customer, 
                    'product_locations_json': product_locations_json,
                    'rating':rating,
                    'productItems':productItems,
                    'customer':customer
                }
                
                    
                return render(request, 'home/shop-detail.html',context)
            except:
                pass
        
        product_locations = list(product.productlocations_set.all().values('location__name', 'quantity'))
        product_locations_json = json.dumps(product_locations)
        context = {
            'product': product, 
            'featured_products': category_products,
            'reviews':reviews,'customer':customer, 
            'product_locations_json': product_locations_json,
            'rating':rating,
            'productItems':productItems,
            'customer':request.user
        }
        
        return render(request, 'home/shop-detail.html',context)
        
    except Product.DoesNotExist:
        return render(request,'404.html')  
    
def category_select(request, catId):
    customer = False
    products = Product.objects.filter(Q(category=catId) & Q(is_active=True))
    for product in products:
        check_offer(product.id)
    
    try:
        productItems = []
        if 'username' in request.session or request.user.is_authenticated:
            customer = request.user
            try:
                cart = Cart.objects.get(user=customer)
                items = CartItem.objects.filter(cart=cart)
                for item in items:
                    productItems.append(item.product)
            except:
                return render(request,'home/user_categories.html',{'products':products,'productItems':productItems,'customer':customer})
            return render(request, 'home/user_categories.html', {"products": products,'customer': customer,'productItems':productItems,'items':items})

    except Category.DoesNotExist:
        return render(request,'404.html')

    return render(request, 'home/usercategories.html', {'products': products})

def filter_product_list(request,sort_by):
    products = None
    if sort_by == 1:
        products = None
    elif sort_by == 2:
        products =  Product.objects.filter(is_active=True).order_by('-selling_price','name')
    elif sort_by == 3:
        products = Product.objects.filter(is_active=True).order_by('selling_price','name')
    elif sort_by == 4:
        products = None
    elif sort_by == 5:
        products = Product.objects.filter(is_active=True).order_by('name')
    elif sort_by == 6:
        products = Product.objects.filter(is_active=True).order_by('-name')
    elif sort_by == 7:
        products = Product.objects.order_by('created_at')
    else:
        products = None

    customer = False
    
    categories = Category.objects.filter(is_active=True).all()
    
    cartitems_product_ids = []
    if 'username' in request.session:
        try:
            customer = vgUser.objects.get(username=request.session['username'])
            cart = None
            cartitems_product_ids = None
            items = None
            customer = vgUser.objects.get(username=request.user.username)
            try:
                cart = Cart.objects.get(user=customer)
                cartitems_product_ids = CartItem.objects.filter(cart=cart).values_list('product_id', flat=True)
                items = CartItem.objects.filter(cart=cart)
            except:
                cart = None
                cartitems_product_ids = None
                items = None
            return render(request, 'home/shop.html', {"products": products,'categories': categories,'customer': customer,'cartitems_product_ids': cartitems_product_ids,'items':items})
        except vgUser.DoesNotExist:
            return render(request,'404.html')
    elif request.user.is_authenticated:
        try:
            customer = vgUser.objects.get(username=request.user.username)
            cart = None
            cartitems_product_ids = None
            items = None
            customer = vgUser.objects.get(username=request.user.username)
            try:
                cart = Cart.objects.get(user=customer)
                cartitems_product_ids = CartItem.objects.filter(cart=cart).values_list('product_id', flat=True)
                items = CartItem.objects.filter(cart=cart)
            except:
                cart = None
                cartitems_product_ids = None
                items = None
            return render(request, 'home/shop.html', {"products": products,'categories': categories,'customer': customer,'cartitems_product_ids': cartitems_product_ids,'items':items})
        except vgUser.DoesNotExist:
            return render(request,'404.html')

    return render(request, 'home/shop.html', {"products": products,'categories': categories,'customer': customer,'cartitems_product_ids': cartitems_product_ids,})

def search_product(request):
    #try:
        if request.method == "POST":
            word = request.POST["search"]
            products = Product.objects.filter(name__istartswith=word).distinct().filter(is_active=True)

            if request.user.is_authenticated:
                try:
                    cart = None
                    cartitems_product_ids = None
                    items = None
                        
                    customer = vgUser.objects.get(username=request.user.username)
                    try:
                        cart = Cart.objects.get(user=customer)
                        cartitems_product_ids = CartItem.objects.filter(cart=cart).values_list('product_id', flat=True)
                        items = CartItem.objects.filter(cart=cart)
                    except:
                        cart = None
                        cartitems_product_ids = None
                        items = None
                    return render(request, 'home/shop.html', {"products": products, 'customer': customer, 'cartitems_product_ids': cartitems_product_ids, 'items': items})
                except vgUser.DoesNotExist:
                    pass
            elif 'username' in request.session:
                try:
                    customer = vgUser.objects.get(username=request.session['username'])
                    cart = None
                    cartitems_product_ids = None
                    items = None
                    try:
                        cart = Cart.objects.get(user=customer)
                        cartitems_product_ids = CartItem.objects.filter(cart=cart).values_list('product_id', flat=True)
                        items = CartItem.objects.filter(cart=cart)
                    except:
                        cart = None
                        cartitems_product_ids = None
                        items = None
                    return render(request, 'home/shop.html', {"products": products, 'customer': customer, 'cartitems_product_ids': cartitems_product_ids, 'items': items})
                except (vgUser.DoesNotExist, Cart.DoesNotExist):
                    pass

            return render(request, 'home/shop.html', {"products": products})

    # except ObjectDoesNotExist as e:
    #     print(f"An error occurred: {e}")
    #     return render(request, '404.html')

    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    #     return render(request, '404.html')
    

