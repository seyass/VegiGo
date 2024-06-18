
####################### module #######################
import pandas as pd
import json
from io import BytesIO
from math import trunc
from django.shortcuts import render, redirect
from authentication.models import vgUser
from authentication.views import signin_page
from ordermanagement import models as Orders
from django.http import HttpResponse, JsonResponse
from . import models
from . import forms
from django.db.models import Sum, F,Count,OuterRef,Subquery
from ordermanagement.models import Order, OrderItem
from productmanagement.models import Product,Category
from datetime import datetime, timedelta,date
from django.utils import timezone
from xhtml2pdf import pisa
from decimal import Decimal
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncDay, TruncMonth, TruncYear, TruncWeek
from django.db import IntegrityError
from django.db.models import Sum, F, Count

####################### addtioanl functions #######################

### sales data
def get_yearly_sales_data():
    today = date.today()
    start_of_year = today.replace(month=1, day=1)
    delivered_orders = Order.objects.filter(created_at__gte=start_of_year, items__status='delivered')
    total_sales = sum(item.subtotal() for order in delivered_orders for item in order.items.all())
    # You can further process data here, like grouping by product name
    return total_sales  # Or a dictionary with product names and sales if needed
def get_monthly_sales_data():
    today = date.today()
    start_of_month = today.replace(day=1)
    delivered_orders = Order.objects.filter(created_at__gte=start_of_month, items__status='delivered')
    total_sales = sum(item.subtotal() for order in delivered_orders for item in order.items.all())
    return total_sales
def get_weekly_sales_data():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    delivered_orders = Order.objects.filter(created_at__gte=start_of_week, items__status='delivered')
    total_sales = sum(item.subtotal() for order in delivered_orders for item in order.items.all())
    return total_sales


####################### admin page #######################

def admin_page(request):
    if 'isusername' in request.session:
        return render(request, 'admin/base.html')
    else:
        return redirect(signin_page)

####################### dashborad and report #######################

def dashboard_page(request):
    if 'isusername' in request.session:
        # Query to get the top 10 best-selling products
        best_selling_product = (
            OrderItem.objects.filter(status='delivered')
            .values('product__product', 'product__category')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:10]
        )

        # Query to get total sales per category
        category_sales = (
            OrderItem.objects.filter(status='delivered')
            .values('product__category')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:10]
        )
        products = Product.objects.all()
        # Prepare context for rendering
        context = {
            'best_selling_product': best_selling_product,
            'category_sales': category_sales,
            'products':products
        }
        
        return render(request, 'admin/dashboard.html', context)

    # If user is not authenticated, redirect to login or handle accordingly
    
def get_dashboard_data(request):

    if 'isusername' not in request.session:
        return redirect(signin_page)

    timeframe = request.GET.get('timeframe', 'weekly')
    product_id = request.GET.get('product', None)

    if timeframe == 'weekly':
        interval = TruncWeek('created_at')
    elif timeframe == 'monthly':
        interval = TruncMonth('created_at')
    else:  # yearly
        interval = TruncYear('created_at')

    orders_query = Order.objects.annotate(interval=interval)
    revenue_query = Order.objects.annotate(interval=interval)

    if product_id:
        orders_query = orders_query.filter(items__key_product_id=product_id)
        revenue_query = revenue_query.filter(items__key_product_id=product_id)

    orders_data = orders_query.values('interval').annotate(total=Count('id')).order_by('interval')
    revenue_data = revenue_query.values('interval').annotate(total=Sum('total_price')).order_by('interval')

    orders_data = [{'date': data['interval'].strftime('%Y-%m-%d'), 'total': data['total']} for data in orders_data]
    revenue_data = [{'date': data['interval'].strftime('%Y-%m-%d'), 'total': data['total']} for data in revenue_data]

    data = {
        'orders_data': orders_data,
        'revenue_data': revenue_data,
    }
    return JsonResponse(data)

def admin_report(request):

    if 'isusername' not in request.session:
        return redirect('signin_page')

    if request.method == 'POST':

        end_date = timezone.now()
        start_date = None
        report_type = request.POST.get('report_type')
        if report_type == 'daily':
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=end_date.day - 1)  # First day of the current month
        elif report_type == 'yearly':
            start_date = end_date.replace(month=1, day=1)  # First day of the current year
        elif report_type == 'custom':
            # Get custom start and end dates from the form
            start_date = request.POST.get('custom_start_date')
            end_date = request.POST.get('custom_end_date')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
           
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())
        
        if start_date and end_date:

            orders = Order.objects.filter(created_at__range=(start_date, end_date))
            order_items = OrderItem.objects.filter(item_created_at__range=(start_date,end_date),status='delivered')
            products = Product.objects.all()
            
            total_quantity = order_items.aggregate(total_quantity=Sum('quantity'))['total_quantity']
            total_revenue = order_items.aggregate(total_revenue=Sum('price'))['total_revenue']
            if total_quantity is None and total_revenue is None:
                total_quantity = 0
                total_revenue = 0
            total_revenue = total_revenue*total_quantity
            
            total_discount = 0 #products.aggregate(total_discount=Sum('max_discount'))['total_discount']
            product_sales = order_items.values('key_product__name').annotate(
                total_sales=Sum(F('price') * F('quantity'))
            ).order_by('-total_sales')
            
            daily_product_sales = order_items.values('order__created_at', 'key_product__name').annotate(
                daily_sales=Sum(F('price') * F('quantity'))
            ).order_by('order__created_at', 'key_product__name')
            df_daily_product_sales = pd.DataFrame(list(daily_product_sales))

            report = f"""
                <h1 style="color: #7755A2; margin-bottom: 20px; text-align: center;">VegiGo Sale Report</h1>

                <h2 style="color: #06A245; text-align: center;">Total Metrics</h2>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #06A245; color: white; text-align: center;">
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td style="text-align: center;">Total Quantity Sold</td>
                        <td style="text-align: center;">{total_quantity}</td>
                    </tr>
                    <tr>
                        <td style="text-align: center;">Total Revenue</td>
                        <td style="text-align: center;">{total_revenue}</td>
                    </tr>
                    <tr>
                        <td style="text-align: center;">Total Discount</td>
                        <td style="text-align: center;">{total_discount}</td>
                    </tr>
                </table>

                <h2 style="color: #06A245; margin-top: 20px; text-align: center;">Product-wise Sales</h2>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #06A245; color: white; text-align: center;">
                        <th>Product</th>
                        <th>Total Sales</th>
                        <th>Quantity Sold</th>
                    </tr>
            """

            # Add product-wise sales to the report with alternating row colors
            row_color = "#FFFFFF"
            for sale in product_sales:
                product = sale['key_product__name']
                product_obj = Product.objects.get(name=product)
                quantity_sold = order_items.filter(key_product=product_obj).aggregate(Sum('quantity'))['quantity__sum']
                report += f"""
                    <tr style="background-color: {row_color}; text-align: center;">
                        <td>{product}</td>
                        <td>${sale['total_sales']}</td>
                        <td>{quantity_sold}</td>
                    </tr>
                """
                # Alternate row colors
                row_color = "#E0E0E0" if row_color == "#FFFFFF" else "#FFFFFF"

            # Include order details, coupon usage, and discount information
            report += """
                </table>

                <h2 style="color: #06A245; margin-top: 20px; text-align: center;">Order Details</h2>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #06A245; color: white; text-align: center;">
                        <th>Order ID</th>
                        <th>User</th>
                        <th>Total Price</th>
                        <th>Coupon Code</th>
                        <th>Coupon Amount</th>
                    </tr>
            """
            for order in orders:
                report += f"""
                    <tr style="text-align: center;">
                        <td>{order.id}</td>
                        <td>{order.user.username}</td>
                        <td>{order.total_price}</td>
                        <td>{order.coupon_code if order.coupon_code else 'N/A'}</td>
                        <td>{order.coupon_amount if order.coupon_amount else 0}</td>
                    </tr>
                """

            report += """
                </table>
            """

            report += """
                <h2 style="color: #06A245; margin-top: 20px; text-align: center;">Daily Product Sales</h2>
                """
            # Append daily product sales data as an HTML table
            report += df_daily_product_sales.to_html(index=False, classes='daily-sales-table', border=0)

            if 'download' in request.POST:
                # Convert HTML report to PDF
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="vegi_go_report.pdf"'
                
                # Use a BytesIO object to create PDF data in memory
                pdf_file = BytesIO()
                
                
                try:
                    pisa_status = pisa.CreatePDF(report, dest=pdf_file)
                except:
                    pisa_status = None
                # If PDF creation was successful, serve the file as a download
                if pisa_status == None:
                    return render(request,'404.html')
                if not pisa_status.err:
                    pdf_file.seek(0)  # Reset file pointer
                    response.write(pdf_file.getvalue())

                    return response
                else:
                    # Return an error message if PDF creation failed
                    return render(request,'404.html')

            # Return the report as an HTTP response
            return render(request,'admin/report_preview.html',{'report':report})
        
        report_data = f"Generating report: Type - {report_type}, Custom Start Date - {start_date}, Custom End Date - {end_date}"

        return HttpResponse(report_data)

    return render(request,'admin/report.html')

####################### branches management #######################

def branches_page(request):

    if 'isusername' not in request.session:
        
        return redirect(signin_page)
    branches = models.Branches.objects.all()
    if request.method == 'POST':
        form = forms.BranchesForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect(branches_page)
        else:
            return render(request,'admin/branch/branch.html',{'form':form,'branches':branches})
    else:
        form = forms.BranchesForm()
        return render(request,'admin/branch/branch.html',{'form':form,'branches':branches})

def edit_branch(request,branchId):
    
    if 'isusername' not in request.session:
        
        return redirect(signin_page)

    branch = models.Branches.objects.get(id=branchId)
    if request.method == 'POST':
        form = forms.BranchesForm(request.POST,instance=branch)
        if form.is_valid():
            form.save()
            return redirect(branches_page)
        else:
            return render(request,'admin/branch/edit_branch.html',{'form':form,'branchId':branchId})
    else:
        form = forms.BranchesForm(instance=branch)

    return render(request,'admin/branch/edit_branch.html',{'form':form,'branchId':branchId})

def delete_branch(request,branchId):

    if 'isusername' not in request.session:
        
        return redirect(signin_page)
    
    branch = models.Branches.objects.get(id=branchId)
    branch.delete()
    return redirect(branches_page)

####################### customers #######################

def customers_page(request):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect(signin_page)

    customers = vgUser.objects.filter(is_superuser=False).all().order_by('username')
    return render(request, 'admin/customers.html', {"customers": customers})

def update_page(request, user_id):
    if 'isusername' not in request.session:
        # Redirect if the user is not logged in
        return redirect(signin_page)

    user = vgUser.objects.get(pk=user_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'active':
            user.is_blocked = False
        elif new_status == 'blocked':
            user.is_blocked = True
        user.save()
        return redirect(customers_page)

    return redirect(customers_page)

####################### coupon management #######################

def coupon_page(request):

    if 'isusername' not in request.session:
        return redirect(signin_page)

    coupons = models.Coupon.objects.all()
    return render(request,'admin/coupon/coupon.html',{'coupons':coupons})

def add_coupon(request):
    if 'isusername' not in request.session:
        return redirect(signin_page)
    
    form = forms.CouponForm()
    if request.method == 'POST':
        form = forms.CouponForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect(coupon_page)
            except IntegrityError:
                form.add_error('code', 'Coupon with this code already exists')
        else:
            return render(request, 'admin/coupon/action_coupon.html', {'form': form})
        return render(request, 'admin/coupon/action_coupon.html', {'form': form})
    
    return render(request, 'admin/coupon/action_coupon.html', {'form': form})
        
def edit_coupon(request, couponId):
    if 'isusername' not in request.session:
        return redirect(signin_page)
    
    coupon = models.Coupon.objects.get(id=couponId)
    form = forms.CouponForm(instance=coupon)
    
    if request.method == 'POST':
        form = forms.CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            try:
                form.save()
                return redirect(coupon_page)
            except IntegrityError:
                form.add_error('code', 'Coupon with this code already exists')
        else:
            return render(request, 'admin/coupon/edit_coupon.html', {'form': form})
        return render(request, 'admin/coupon/edit_coupon.html', {'form': form})
    
    return render(request, 'admin/coupon/edit_coupon.html', {'form': form}) 

def delete_coupon(request,couponId):

    if 'isusername' not in request.session:
        return redirect(signin_page)

    coupon = models.Coupon.objects.get(id=couponId)
    coupon.delete()
    return redirect(coupon_page)


