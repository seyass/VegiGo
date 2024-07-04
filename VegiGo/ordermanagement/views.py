
from django.shortcuts import render,redirect
from customer.models import CartItem,UserAddress,Wallet
from ordermanagement import models as Orders
from productmanagement import models as Products
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from productmanagement.forms import ReviewForm,Review
from django.conf import settings
import razorpay
from decimal import Decimal
from customer.views import cart_page
from .models import Order,OrderItem
from vgadmin.models import Coupon
import json
from vgadmin.models import Branches
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
# Create your views here.
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def generate_invoice(order):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Define colors
    purple = HexColor("#7755A2")
    green = HexColor("#06A245")
    black = HexColor("#000000")
    white = HexColor("#FFFFFF")

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(purple)
    c.drawString(30, height - 50, "Invoice")

    # Order details
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(30, height - 100, f"Order ID: {order.id}")
    c.drawString(30, height - 120, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
    c.drawString(30, height - 140, f"Customer: {order.user.username}")
    c.drawString(30, height - 160, f"Payment Method: {order.payment_method}")

    # address
    address_x = width - 250  # Adjust this value to position the address
    c.drawString(address_x, height - 100, "Shipping Address:")
    c.drawString(address_x, height - 120, f"{order.address_info['street_address']}")
    c.drawString(address_x, height - 140, f"{order.address_info['city']}")
    c.drawString(address_x, height - 160, f"{order.address_info['district']}, {order.address_info['pincode']} {order.address_info['landmak']}")
    c.drawString(address_x, height - 180, f"{order.address_info['phone_number']}")
    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(white)
    c.setStrokeColor(green)
    c.setFillColor(purple)
    c.rect(30, height - 210, 540, 20, fill=1)
    c.setFillColor(white)
    c.drawString(35, height - 205, "Product")
    c.drawString(100,height - 205, "Price")
    c.drawString(200, height - 205, "Discount")
    c.drawString(300, height - 205, "Buy Price")
    c.drawString(400, height - 205, "Quantity")
    c.drawString(500, height - 205, "Subtotal")

    # Order items
    y = height - 240
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    for item in order.items.all():
        c.drawString(35, y, item.key_product.name)
        c.drawString(100, y, f"{item.key_product.price:.2f}")
        c.drawString(200, y, f"{item.discount:.2f}")
        c.drawString(300, y, f"{item.price:.2f}")
        c.drawString(400, y, str(item.quantity))
        c.drawString(500, y, f"{item.subtotal():.2f}")
        y -= 20

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(purple)
    c.drawString(400, y - 20, "Coupon:")
    c.drawString(500, y - 20, str(order.coupon_code))
    c.drawString(400, y - 40, "Amount:")
    c.drawString(500, y - 40, f"{order.coupon_amount:.2f}")
    c.drawString(400, y - 60, 'Discount:')
    c.drawString(500, y - 60, f"{order.total_discount:.2f}")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(400, y - 100, "Total:")
    c.drawString(500, y - 100, f"{order.total_price:.2f}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def place_order(request):
    
    #try:
    if request.method == "POST":

        cart = request.user.cart
        items = CartItem.objects.filter(cart=cart)
        if cart.location:
            for item in items:
                q = Products.ProductLocations.objects.filter(product=item.product,location=cart.location)
                if q.exists():
                    for i in q:
                        if i.quantity == 0:
                            item.quantity = 0
                            return redirect('cart_page')
                        elif i.quantity < item.quantity:
                            item.quantity = i.quantity
                            return redirect('cart_page')
                else:
                    return redirect('cart_page')
        if cart.select_coupon:
            coupon = cart.select_coupon
            coupon.used_by_users.set([request.user])
            coupon.save()
        #try:
        selected_address = request.POST.get('address')
        selected_address = UserAddress.objects.get(id=selected_address)
        selected_payment = request.POST.get('paymentMethod')
        address_data = {
            'firstname':selected_address.firstname,
            'lastname':selected_address.lastname,
            'city':selected_address.city,
            'landmak':selected_address.landmark,
            'phone_number':selected_address.phone_number,
            'district':selected_address.district.name,
            'street_address':selected_address.street_address,
            'pincode':selected_address.pincode
        }
        if selected_payment == 'Razorpay':
                # Create order data for Razorpay
            order_amount = int(cart.sub_total * 100)  # Amount in paise
            order_currency = 'INR'
            order_data = {
                'amount': order_amount,
                'currency': order_currency,
                'payment_capture': '1'
                
            }
            
            request.session['selected_address_id'] = {'id':selected_address.id}
            
            # Create order in Razorpay
            razorpay_order = client.order.create(data=order_data)
            order_id = razorpay_order['id']
            request.session['razorpay_id'] = order_id
            request.session['razorpay'] = 'active'
            cart = request.user.cart
            items = cart.items.all()
            cart.calculate_total_price()
            cart.save()
            # Payment verification successful
            # Retrieve the order from your database
            address_data = {
                'firstname':selected_address.firstname,
                'lastname':selected_address.lastname,
                'city':selected_address.city,
                'landmak':selected_address.landmark,
                'phone_number':selected_address.phone_number,
                'district':selected_address.district.name,
                'street_address':selected_address.street_address,
                'pincode':selected_address.pincode
            }
            
            adminOrder = Orders.Order.objects.create(
                    user = request.user,
                    address_info = address_data,
                    payment_method = selected_payment,
                    total_price = cart.sub_total,   
                    razorpayId=order_id,
                    order_payment_status = 'pending'    
                )
            if cart.select_coupon:
                adminOrder.coupon_code = cart.select_coupon.code
                adminOrder.coupon_amount = cart.select_coupon.discount_amount
                adminOrder.save()

            for cart_item in items:
                product_data = {
                        'product':cart_item.product.name,
                        'category':cart_item.product.category.name,
                        'unit_type':cart_item.product.unit_type
                    }
                Orders.OrderItem.objects.create(
                    key_product=cart_item.product,
                    order=adminOrder,
                    product=product_data,
                    price=cart_item.product.special_discount,  # or use cart_item.product.selling_price if applicable
                    image = cart_item.product.primary_image,
                    quantity=cart_item.quantity,
                    status='pending',
                    payment_status='failed',
                    discount=cart_item.product.max_discount
                )
                product = Products.ProductLocations.objects.filter(product=cart_item.product,location=selected_address.district.id)
                for i in product:
                    i.quantity = i.quantity - cart_item.quantity
                    i.save()
            # Render payment page with Razorpay checkout script
            cart.delete()
            return render(request, 'customer/orders/payment.html', {
                'order_id': order_id,
                'amount': order_amount,
                'key_id': settings.RAZORPAY_KEY_ID
            })
        
        elif selected_payment == "Wallet":
            
            if request.user.wallet.amount < cart.sub_total:
                msg = "The wallet not have much balance"
                return render(request,'404.html',{'msg':msg})
            else:
                
                wallet = Wallet.objects.get(user=request.user)
                wallet.previous_balance = wallet.amount
                wallet.amount -= cart.sub_total
                wallet.save()
    
                order = Orders.Order.objects.create(
                user = request.user,
                address_info = address_data,
                payment_method = selected_payment,
                total_price = cart.sub_total,
                order_payment_status = 'completed',
                )   
                if cart.select_coupon:
                    order.coupon_code = cart.select_coupon.code
                    order.coupon_amount = cart.select_coupon.discount_amount
                    order.save()
                for cart_item in items:
                    product_data = {
                        'product':cart_item.product.name,
                        'category':cart_item.product.category.name,
                        'unit_type':cart_item.product.unit_type
                    }
                    orderitem = Orders.OrderItem.objects.create(
                        key_product=cart_item.product,
                        order=order,
                        product=product_data,
                        price=cart_item.product.special_discount,  # or use cart_item.product.selling_price if applicable
                        image = cart_item.product.primary_image,
                        quantity=cart_item.quantity,
                        status='pending',
                        payment_status='Completed',
                        discount=cart_item.product.max_discount
                        
                    )
                    product = Products.ProductLocations.objects.filter(product=cart_item.product,location=selected_address.district.id)
                    for i in product:
                        i.quantity = i.quantity - cart_item.quantity
                        i.save()

                cart.delete() 
            return render(request,'customer/orders/order_success_page.html')
        
        else:

            if cart.sub_total > 1000:
                return render(request,'404.html')
            try:
                order = Orders.Order.objects.create(
                    user = request.user,
                    address_info = address_data,
                    payment_method = selected_payment,
                    total_price = cart.sub_total,
                    order_payment_status = 'pending'
                )
            except Exception as e:
                print(e)
                return render(request,'404.html')
            if cart.select_coupon:
                order.coupon_code = cart.select_coupon.code
                order.coupon_amount = cart.select_coupon.discount_amount
                order.save()
            for cart_item in items:
                product_data = {
                    'product':cart_item.product.name,
                    'category':cart_item.product.category.name,
                    'unit_type':cart_item.product.unit_type
                }
                Orders.OrderItem.objects.create(
                    key_product=cart_item.product,
                    order=order,
                    product=product_data,
                    price=cart_item.product.special_discount,  # or use cart_item.product.selling_price if applicable
                    image = cart_item.product.primary_image,
                    quantity=cart_item.quantity,
                    status='completed',
                    payment_status='pending',
                    discount=cart_item.product.max_discount
                )
                product = Products.ProductLocations.objects.filter(product=cart_item.product,location=selected_address.district.id)
                for i in product:
                    i.quantity = i.quantity - cart_item.quantity
                    i.save()
            
            cart.delete()        
            return render(request,'customer/orders/order_success_page.html')    
            
            # except Exception as e:
            #     print(e)
            #     render(request,'404.html')
    # except Exception as e:
    #     print(e)
    #     return render(request,'404.html')
    return render(request,'404.html')

def failed_payment(request,orderId):

    if request.user.is_authenticated:

        order = Order.objects.get(id=orderId)
        razorpay_order = client.order.create({
            'amount': int(order.total_price * 100),  # amount in paisa
            'currency': 'INR',
            'payment_capture': '1'
        })
        
        # Save the new Razorpay order ID
        order.razorpayId = razorpay_order['id']
        request.session['razorpay_id'] = order.razorpayId
        order.save()

        context = {
            'order_id': order.razorpayId,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': order.total_price * 100, 
        }

        return render(request, 'customer/orders/payment.html',context)
    
    else:
        return render(request, '404.html')

def handle_webhook(request):

    if request.method == 'POST':

        data = request.body.decode('utf-8')
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # Verify the signature
    if client.utility.verify_webhook_signature(data, request.META['HTTP_X_RAZORPAY_SIGNATURE']):
      # Parse the JSON data
        payment_data = json.loads(data)
      
      # Check for failed payment
        if payment_data['status'] == 'failed':
            print('ivde vannuta')
        # Update your models and send notifications (logic here)
            return JsonResponse({'message': 'Payment failed. Processing initiated.'})
        else:
        # Handle other payment statuses if needed
            return JsonResponse({'message': 'Unexpected payment status.'})
    else:
      # Handle invalid signature
      return JsonResponse({'message': 'Invalid webhook signature.'}, status=400)
 
def order_success(request):

    if request.user.is_authenticated or 'username' in request.session:
        return render(request,'customer/orders/order_success_page.html')
    else:
        return redirect('signin_page')

def user_order_cancel(request,orderItemId):

    if request.user.is_authenticated or 'username' in request.session:
        
        order = Orders.OrderItem.objects.get(id=orderItemId)
        main_order = Order.objects.get(id=order.order.id)
        if order.status == 'Cancelled':
            return redirect('orders_page')
        
        amount = 0
        if order.payment_status == 'Completed':
            
            if order.order.coupon_amount and order.order.coupon_amount>0:
                coupon = Coupon.objects.get(code=order.order.coupon_code)
                main_order.total_price -= order.subtotal()
                main_order.save()
                if main_order.total_price < coupon.minimum_purchase:
                    try:
                        coupon = Coupon.objects.get(code=order.order.coupon_code)
                        main_order.coupon_amount = 0
                        main_order.coupon_code = None
                        amount = order.subtotal() - order.order.coupon_amount
                        coupon.used_by_users.remove(request.user)
                        coupon.save()
                    except:
                        amount = order.subtotal() - order.order.coupon_amount
                else:
                    amount = order.subtotal()
            else:
                amount = order.subtotal()
        if amount:
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            amount = Decimal(amount)
            wallet.previous_balance = wallet.amount
            wallet.amount += amount
            wallet.save()
        order.status = 'cancelled'
        item_total = order.subtotal()
        order.order.total_price = order.order.total_price - item_total
        order.order.save()
        order.user_cancel = True
        order.payment_status = 'Completed'
        location_name = order.order.address_info.get('district')
        location = Branches.objects.get(name=location_name)
        product = order.key_product
        product = Products.ProductLocations.objects.filter(product=product,location=location)
        for i in product:
            i.quantity = i.quantity + order.quantity
            i.save()
            
        order.save()
        return redirect('orders_page')
    else:
        return redirect('signin_page')

def admin_orders(request):

    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect('signin_page')
    vbn = {'A':'a','B':'b','C':'c'}
    
    orders = Orders.Order.objects.all().order_by('-id')
    order_item = []
    for order in orders:
        order_item.append(Orders.OrderItem.objects.filter(order=order))
    
            
    return render(request,'admin/orders/orders.html',{'order_item':order_item,'orders':orders})

def admin_order_detail(request,orderId):

    if 'isusername' in request.session:

        order = Order.objects.get(id=orderId)
        items = order.items.all()
        return render(request,'admin/orders/order_detail.html',{'items':items,'order':order})


def return_request(request,itemId):

    if request.user.is_authenticated or 'username' in request.session:

        item = OrderItem.objects.get(id=itemId)
        item.status = 'Return Requested'
        item.save()
        
        return redirect('orders_page')
    else:
        return redirect('signin_page')

@csrf_exempt
def update_order_status(request):

    if request.user.is_authenticated or 'username' in request.session:
        if request.method == 'POST':
            
            order_item_id = request.POST.get('order_item_id')
            new_status = request.POST.get('new_status')
            order_item = OrderItem.objects.get(id=order_item_id)
            if order_item.status == 'cancelled' or order_item.status == 'returned' or order_item.status == 'delivered':
                return JsonResponse({'error': 'Invalid request method'}, status=400)
            if new_status == 'returned':
                order_item = OrderItem.objects.get(id=order_item_id)
                order_item.status = 'returned'
                order_item.save()
                wallet, created = Wallet.objects.get_or_create(user=order_item.order.user)
                wallet.amount += Decimal(str(order_item.subtotal()))
                wallet.save()
                location_name = order_item.order.address_info.get('district')
                location = Branches.objects.get(name=location_name)
                product = order_item.key_product
                product = Products.ProductLocations.objects.filter(product=product,location=location)
                for i in product:
                    i.quantity = i.quantity + order_item.quantity
                    i.save()
            elif new_status == 'cancelled':
                order = OrderItem.objects.get(id=order_item_id)
                main_order = Order.objects.get(id=order.order.id)
                amount = 0
                if order.payment_status == 'Completed':
                    if order.order.coupon_amount and order.order.coupon_amount>0:
                        coupon = Coupon.objects.get(code=order.order.coupon_code)
                        main_order.total_price -= order.subtotal()
                        main_order.save()
                        if main_order.total_price < coupon.minimum_purchase:
                            try:
                                coupon = Coupon.objects.get(code=order.order.coupon_code)
                                main_order.coupon_amount = 0
                                main_order.coupon_code = None
                                amount = order.subtotal() - order.order.coupon_amount
                                coupon.used_by_users.remove(order.order.user)
                                coupon.save()
                            except:
                                amount = order.subtotal() - order.order.coupon_amount
                        else:
                            amount = order.subtotal()
                    else:
                        amount = order.subtotal()
                if amount:
                    wallet, created = Wallet.objects.get_or_create(user=order.order.user)
                    wallet.previous_balance = wallet.amount
                    wallet.amount += amount
                    wallet.save()
                order.status = 'cancelled'
                order.user_cancel = True
                order.payment_status = 'Completed'
                location_name = order.order.address_info.get('district')
                location = Branches.objects.get(name=location_name)
                product = order_item.key_product
                product = Products.ProductLocations.objects.filter(product=product,location=location)
                for i in product:
                    i.quantity = i.quantity + order.quantity
                    i.save()   
                order.save()
            elif new_status == 'delivered':
                order = OrderItem.objects.get(id=order_item_id)
                if order.order.payment_method == 'cod':
                    order = OrderItem.objects.get(id=order_item_id)
                    item_total = order.subtotal()
                    order.status = 'delivered'
                    order.order.total_price = order.order.total_price - item_total
                    order.order.save()
                    if order.order.total_price <= 0:
                        order.order.total_price = 0
                        order.order.order_payment_status = 'completed'
                        order.order.save()
                    
            try:
                order_item = Orders.OrderItem.objects.get(id=order_item_id)
                order_item.status = new_status
                order_item.save()

                return JsonResponse({'success': True},status=200)

            except Orders.OrderItem.DoesNotExist:
                
                return JsonResponse({'error': 'Order item not found'}, status=404)

            except Exception as e:
                
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'error': 'Invalid request method'}, status=400)
    else:
        return redirect('signin_page')

def user_review(request,orderItemId):

    if request.user.is_authenticated or 'username' in request.session:

        item = Orders.OrderItem.objects.get(id=orderItemId)
        print(item.product)
        product = Products.Product.objects.get(name=item.product)

        if request.method == 'POST':
            form = ReviewForm(request.POST,request.FILES)
            if form.is_valid():
                rating = form.cleaned_data['rating']
                content = form.cleaned_data['content']
                Review.objects.create(
                    user = request.user,
                    product = product,
                    rating = rating,
                    content = content
                )

                return redirect('orders_page')
            
    else:
        return redirect('signin_page')




    form = ReviewForm()

    return render(request,'customer/orders/review.html',{'form':form})

@csrf_exempt
def verify_payment(request):

    if request.user.is_authenticated or 'username' in request.session:

        if request.method == 'POST':
        # Retrieve the payment response data from the request
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            razorpay_id = request.session['razorpay_id']
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            # Verify the payment signature using the Razorpay client
            try:
                client.utility.verify_payment_signature({
                    'razorpay_payment_id': payment_id,
                    'razorpay_order_id': order_id,
                    'razorpay_signature': signature
                })
                order = Orders.Order.objects.get(razorpayId=razorpay_id)
     
                order_items = Orders.OrderItem.objects.filter(order=order)
                for item in order_items:
                    item.status = 'Completed'
                    item.payment_status = 'Completed'
                    item.save()
                order.order_payment_status = 'completed'
                order.save()
                if 'razorpay' in request.session:
                    del request.session['razorpay']
                del request.session['razorpay_id']
                return render(request,'customer/orders/order_success_page.html')
            
            except razorpay.errors.SignatureVerificationError:
                order.order_payment_status = 'failed'
                order.save()
                if 'razorpay' in request.session:
                    del request.session['razorpay']
                del request.session['razorpay_id']

                return render(request,'customer/orders/order_failed_page.html')
            
            except:
                order.order_payment_status = 'failed'
                order.save()
                del request.session['razorpay']
                return render(request,'customer/orders/order_failed_page.html')
    else:
        return redirect('signin_page')

def download_invoice(request, orderId):

    if request.user.is_authenticated:
        order = Order.objects.get(id=orderId)
        buffer = generate_invoice(order)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response


