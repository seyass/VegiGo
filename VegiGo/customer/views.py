####################### modules #######################

from django.utils import timezone
from django.shortcuts import render,redirect
from django.urls import reverse
from home.views import home_page,check_offer
from authentication.models import vgUser
from vgadmin.models import Branches,Coupon
from .forms import UserProfileForm , AddressForm
from .models import Cart,CartItem,UserAddress,Wallet,WalletHistory
from django.core.exceptions import ObjectDoesNotExist
from productmanagement.models import Product,ProductLocations
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register
from ordermanagement import models as Orders
from django.contrib.auth import authenticate,login
from .models import Wishlist,WishlistItem


####################### user profile #######################

def user_profile(request):
    
    if request.user.is_authenticated:
        try:
            customer = request.user
            return render(request,'customer/profile/profile.html',{'customer':customer})
        except:
            return render(request,'404.html')
    else:
        return redirect('signin_page')

def edit_profile(request):

    if request.user.is_authenticated:
        customer = request.user
        if customer.is_superuser is False:
            if request.method == 'POST':
                form = UserProfileForm(request.POST, instance=request.user)
                if form.is_valid():
                    form.save()
                    return redirect('user_profile')  
                else:
                    return render(request, 'customer/profile/edit_profile.html', {'form': form,'customer':customer})# Redirect to profile page after successful form submission
            else:
                form = UserProfileForm(instance=customer)
                return render(request, 'customer/profile/edit_profile.html', {'form': form,'customer':customer})
        else:
            return render(request, "404.html")
        
    else:
        return render(request,'404.html')

def edit_password(request):

    if request.user.is_authenticated:
        
        msg = None
        user = request.user
        if request.method == 'POST':
            old_password = request.POST.get('oldpassword')
            new_password = request.POST.get('newpassword')
            password_check = new_password.strip()
            if len(password_check)<6:
                msg = 'Password need minimum 6 character'
                return render(request,'customer/profile/edit_password.html',{'msg':msg})
            authenticated_user = authenticate(username=user.username, password=old_password)
            
            if authenticated_user:
                user.set_password(new_password)
                user.save()
                authenticated_user = authenticate(username=user.username, password=new_password)
                if authenticated_user:    
                    login(request, authenticated_user, backend=authenticated_user.backend)
                    return redirect('user_profile')
                else:
                    return redirect('signin_page')  
            else:
                msg = 'The password old_password  is incorrect.'
                return render(request,'customer/profile/edit_password.html',{'msg':msg})
        return render(request,'customer/profile/edit_password.html',{'msg':msg})
    return redirect('user_profile')  
    
#######################  address ####################### 

def address_page(request):

    if request.user.is_authenticated:
        user = request.user 
        addresses = UserAddress.objects.filter(user=user)
        userAddress = addresses.exists()
        print(userAddress)
        if request.method == 'POST':
            form = AddressForm(request.POST)
            if form.is_valid():
                
                form.instance.user = user
                form.save()
                return_url = request.GET.get('return_url')
                if return_url == 'checkout_page':
                    return redirect('checkout_page',request.user.cart.id)
                else:
                    form = AddressForm()
                    return redirect(reverse('address_page'))
            else:
                form = AddressForm()
                return render(request,'customer/profile/address.html',{'userAddress':userAddress,'addresses':addresses,'form':form})
        else:
            form = AddressForm()
            return render(request,'customer/profile/address.html',{'userAddress':userAddress,'addresses':addresses,'form':form})
        
    else:
        return redirect('signin_page')

def edit_address(request, addressId):

    if request.user.is_authenticated:
    
        address = UserAddress.objects.get(pk=addressId)
        addresses = UserAddress.objects.filter(user=request.user).order_by("-address_type")
        userAddress = addresses.exists() 
        if request.method == "POST":
            form = AddressForm(request.POST, instance=address)
            
            if form.is_valid():
                form.save()  # Save the changes to the address
                return redirect('address_page')  
            else:
                return render(request, "customer/profile/edit_address.html", {'form': form,'addresses':addresses,'userAddress':userAddress}) # Redirect to address detail page
        else:
            # If the request is GET, populate the form with the address data
            form = AddressForm(instance=address)
        
        if addresses is None:
            userAddress = False
        else:
            userAddress = True
        return render(request, "customer/profile/edit_address.html", {'form': form,'addresses':addresses,'userAddress':userAddress})
    else:
        return redirect('signin_page')

def delete_address(request,addressId):

    if request.user.is_authenticated:
        try:
            address = UserAddress.objects.get(id=addressId)
            address.delete()
        except:
            pass
        return redirect('address_page')
    else:
        return redirect('signin_page')

####################### cart management  #######################

def cart_page(request):

    # Check if the user is authenticated or if the username is in the session
    if request.user.is_authenticated or 'username' in request.session:
        branches = Branches.objects.filter(is_active=True)
        try:
            cart = Cart.objects.get(user=request.user)
            items = CartItem.objects.filter(cart=cart).order_by('product__name')
            # Annotate the maximum quantity available for each product at the selected branch
            if cart.location:
                for item in items:
                    q = ProductLocations.objects.filter(product=item.product,location=cart.location)
                    if q.exists():
                        for i in q:
                            if item.quantity > i.quantity:
                                item.quantity = i.quantity
                            item.max_quantity = i.quantity
                    else:
                        item.max_quantity = 0
                    item.save()
                    
            for product in items:
                product.product = check_offer(product.product.id)
                product.save()

            total_price = sum(item.product.price * item.quantity for item in items)
            total_selling_price = 0
            for item in items:
                total_selling_price += item.total_price
            total_discount = total_price - total_selling_price
            grand_total = total_price - total_discount
            return render(request, "customer/cart.html", {"items": items,'cart':cart,
                'total_price': total_price,
                'total_discount': total_discount,
                'grand_total': grand_total,
                "cartId":cart.id,
                'branches':branches,
                
                })

        except ObjectDoesNotExist:
            items = []
            return render(request, "customer/cart.html", {'items': items,'cartId':None,'branches':branches})
    else:
        return redirect(home_page)

def add_to_cart(request,productId):

    if 'username' in request.session or request.user.is_authenticated:
        
        quantity = 1
        product = Product.objects.get(id=productId)
        user = request.user
        locations = ProductLocations.objects.filter(product=product)
        for location in locations:
            if location.quantity > 0:
                quantity = 1
                break
            else:
                quantity = 0
        user_cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, _ = CartItem.objects.get_or_create(cart=user_cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        return redirect('cart_page')
    else:
        return redirect('signin_page')

def remove_cart_item(request, item_id):

    if request.user.is_authenticated or 'username' in request.session:
        item = CartItem.objects.get(id=item_id)
        cart = item.cart
        item.delete()
        return redirect('cart_page')
    else:
        # Handle case where user is not authenticated
        return redirect(home_page)

def add_to_cart_wishlist(request,productId):

    product = Product.objects.get(id=productId)
    try:
        cartItem = request.user.cart.items.all()
        for item in cartItem:
            print(item.product)
            if item.product == product:
                print('cart')
                return redirect('cart_page')
    except:
        pass
    
    user_cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, _ = CartItem.objects.get_or_create(cart=user_cart, product=product)
    locations = ProductLocations.objects.filter(product=product)
    
    quantity = 1
    for location in locations:
        if location.quantity > 0:
            quantity = 1
            break
        else:
            quantity = 0
    cart_item.quantity += quantity
    cart_item.save()
    return redirect('cart_page')

@csrf_exempt
def update_cart_item(request):

    if request.method == 'POST':
        
        cart_id = request.POST.get('cart_id')
        product_id = request.POST.get('product_id')
        product = check_offer(product_id)
        new_quantity = int(request.POST.get('new_quantity'))
        branchId = request.POST.get('branch_id')
        branch = None
        if branchId:
            branch = Branches.objects.get(id=branchId)
        else:
            return JsonResponse({'error': 'Please select a location'}, status=404)
        
        max_quantity_qs = ProductLocations.objects.filter(product_id=product_id, location_id=branchId).values_list('quantity', flat=True)
        max_quantity = max_quantity_qs.first() if max_quantity_qs.exists() else None
        if max_quantity:
            if new_quantity > max_quantity:
                return JsonResponse({'error': 'The quantity limits exceeds'}, status=404)
        
        
        try:
            cart_item = CartItem.objects.get(cart=request.user.cart, product_id=product_id)
            cart_item.quantity = new_quantity
            cart_item.save()
            cart = Cart.objects.get(id=cart_id)
            item_total = 0
            
            items = cart.items.all()
            for item in items:
                lo = item.product.productlocations_set
                q = ProductLocations.objects.filter(product=item.product,location=Branches.objects.get(id=branchId))
                if q.exists():
                    for i in q:
                        item.max_quantity = i.quantity
                else:
                    item.max_quantity = 0
                item.save()
            total_selling_price = 0
            
                
            for item in items:
                total_selling_price += item.total_price

            total_price = sum(item.product.price * item.quantity for item in items)
            item_total = cart_item.total_price

            total_discount = total_price - total_selling_price
            grand_total = total_price - total_discount
            cart = Cart.objects.get(id=cart_id)
            cart_total = sum(item.quantity * item.product.price for item in cart.items.all())
            cart.calculate_total_price
            cart.save()
            print(cart.sub_total)
            return JsonResponse({
                'new_quantity': cart_item.quantity,
                'item_total': item_total,
                'cart_total': cart_total,
                'grand_total': grand_total,
                'total_discount':total_discount,
            })

        except CartItem.DoesNotExist:
        
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def update_cart_location(request):

    if request.method == "POST":
        print('ivedecedececdee')
        cart_id = request.POST.get('cart_id')
        branch_id = request.POST.get('branch_id')
        try:
            cart = Cart.objects.get(id=cart_id)
        except:
            return render(request,'404.html')
        items = cart.items.all()
        # set maximum quantity with selected location
        for item in items:
            q = ProductLocations.objects.filter(product=item.product,location=Branches.objects.get(id=branch_id))
            if q.exists():
                for i in q:
                    if i.quantity == 0:
                       item.quantity = 0
                    else:
                       item.max_quantity = i.quantity
                       item.quantity = 1
            else:
                item.max_quantity = 0
                item.quantity = 0
            item.save()
            
        cart.location = Branches.objects.get(id=branch_id)
        cart.save()
        return redirect('cart_page')

####################### checkout and orders  #######################

def checkout_page(request,cartId):

    try:
        cart = request.user.cart
        items = cart.items.all()
        now = timezone.now()
    except:
        cart = None
        items = None
    try:
        available_coupons = Coupon.objects.filter(
        minimum_purchase__lte=cart.sub_total,
        start_date__lte = now,
        end_date__gte=now
        ).exclude(
            used_by_users=request.user
        )
    except:
        available_coupons = None
    for item in items:
        if item.quantity < 1:
            return redirect('cart_page')


    if 'razorpay' in request.session:
        order_id = request.session['razorpay_id']
        order = Orders.Order.objects.get(razorpayId = order_id)
        order_items = Orders.OrderItem.objects.filter(order=order)
        order.order_payment_status = 'failed'
        order.save()
        for item in order_items:
            item.payment_status = 'failed'
            item.save()
        del request.session['razorpay']
        return render(request,'customer/orders/order_failed_page.html')

    if cartId is False:
        return render(request,'authenication/signin.html')

    if request.user.is_authenticated:
        
        try:
            
            items = cart.items.all()
            if cart.location:
                for item in items:
                    q = ProductLocations.objects.filter(product=item.product,location=cart.location)
                    if q.exists():
                        for i in q:
                            if i.quantity == 0:
                                item.quantity = 0
                                return JsonResponse({'error':'There is a product out of stock'})
                            elif i.quantity < item.quantity:
                                item.quantity = i.quantity
                                return JsonResponse({'error':'There is a quantity mismatching'})
                    else:
                        return JsonResponse({'error':'There is a product out of stock'})
                    
            else:
                return JsonResponse({'error':'please set a location'})
            for product in items:
                product.product = check_offer(product.product.id)
                product.save()
                
                
            customer = cart.user
            addresses = UserAddress.objects.filter(user=customer.id,district=cart.location)
            
            total_price = sum(item.product.price * item.quantity for item in items)
            total_selling_price = sum(item.product.special_discount * item.quantity for item in items)
            total_discount = total_price - total_selling_price
            grand_total = total_price - total_discount
            return render(request, "customer/checkout.html", {"items": items, 'cart':cart,
                'total_price': total_price,
                'total_discount': total_discount,
                'grand_total': grand_total,
                "cartId":cart.id,
                'addresses':addresses,
                'customer':customer,
                'coupons':available_coupons})
        except ObjectDoesNotExist:
            items = []
            cartId = None
            return render(request, "customer/checkout.html", {'items': items,'cartId':cartId,'coupons':available_coupons})
    else:
        return redirect(home_page)

@csrf_exempt
def apply_coupon(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            code = request.POST.get('coupon_code')
            user = request.user
            coupon = Coupon.objects.get(code=code)
            if coupon.end_date < timezone.now().date() or coupon.start_date > timezone.now().date():
                return JsonResponse({'error':'This coupon out of date range'})
            try:
                usedCoupon = Coupon.objects.filter(used_by_users=user)
                if coupon in usedCoupon:
                    return JsonResponse({'error':'already used this coupon'})
            except:
                pass
            cart = Cart.objects.get(user=user)
            if cart.select_coupon:
                return JsonResponse({'error':'Already use one coupon'})
            sub_total = cart.sub_total
            items = cart.items.all()
            if coupon:
                for item in items:
                    if item.total_price < coupon.discount_amount:
                        error_message = f"The  total purchase amount does not meet the minimum required of {coupon.discount_amount}."
                        return JsonResponse({'error':error_message})
                
                if coupon.minimum_purchase > sub_total:
                    error_message = f"The  total purchase amount does not meet the minimum required of {coupon.minimum_purchase}."
                    return JsonResponse({'error':error_message})
            
            cart.select_coupon = coupon
            cart.calculate_total_price()
            cart.save()
            return JsonResponse({'success':True})
    else:
        return redirect('signin_page')

def remove_coupon(request):
    
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)
        cart.select_coupon = None
        cart.calculate_total_price()
        cart.save()
        
        return redirect('checkout_page',cart.id)

def orders_page(request):

    if request.user.is_authenticated:

        orders = Orders.Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'customer/orders/orders.html',{'orders':orders})
    else:
        return render(request,'404.html')

def order_detail(request,orderId):

    if request.user.is_authenticated:

        order = Orders.Order.objects.get(id=orderId)
        items = Orders.OrderItem.objects.filter(order=order)
        
        return render(request,'customer/orders/order_detail.html',{'items':items,'order':order})

####################### wishlist #######################

def wishlist_page(request):

    if request.user.is_authenticated:
        
        user = None
        if request.user.is_authenticated:
            user = request.user
        else:
            user = vgUser.objects.get(username=request.session['username'])
        items = None
        wishlistItems = None
        try:
            wishlist = Wishlist.objects.get(user=user)
            wishlistItems = WishlistItem.objects.filter(wishlist=wishlist)
            items = user.cart.items.values_list('product')
        except:
            pass
        
        return render(request,'customer/wishlist.html',{'wishlistItems':wishlistItems,'items':items})
    
    else:
        return redirect('signin_page')

def add_wishlist(request, productId):
    if request.user.is_authenticated:
        user = None
        if request.user.is_authenticated:
            user = request.user
        else:
            user = vgUser.objects.get(username=request.session['username'])
        product = Product.objects.get(id=productId)

        wishlist, created = Wishlist.objects.get_or_create(user=user)
        if created:
            try:
                wishlist_item, created_item = WishlistItem.objects.get_or_create(
                    wishlist=created,
                    product=product
                )
                if created_item:
                    msg = "Product added to wishlist"
                else:
                    msg = "Product already exists in wishlist"
            except:
                msg = "An error occurred"

        try:
            wishlist_item, created_item = WishlistItem.objects.get_or_create(
                wishlist=wishlist,
                product=product
            )
            if created_item:
                msg = "Product added to wishlist"
            else:
                msg = "Product already exists in wishlist"
        except:
            msg = "An error occurred"

        wishlist = Wishlist.objects.get(user=user)
        wishlistItems = WishlistItem.objects.filter(wishlist=wishlist)
        return render(request, 'customer/wishlist.html', {'msg': msg,'wishlistItems':wishlistItems})
        
    return render(request,'404.html')

def delete_wishlist(request,productId):

    if request.user.is_authenticated:
        user = None
        if request.user.is_authenticated:
            user = request.user
        else:
            user = vgUser.objects.get(username=request.session['username'])
        product = Product.objects.get(id=productId)
        wishlist = Wishlist.objects.get(user=user)
        wishlistitem = WishlistItem.objects.get(wishlist=wishlist,product=product)
        wishlistitem.delete()
        return redirect('wishlist_page')

####################### wallet #############################

def wallet_page(request):
    user = None
    if request.user.is_authenticated:
        
        user = request.user
        try:
            wallet = Wallet.objects.get(user=user)
            wallet_history = WalletHistory.objects.filter(wallet=wallet).order_by('-timestamp')
        except:
            wallet = None
            wallet_history = None
            pass
        
        return render(request,'customer/profile/wallet.html',{'wallet':wallet,'wallet_history':wallet_history})

####################### others #############################

@register.filter
def get_item(dictionary,key):
    return dictionary.get(key)











