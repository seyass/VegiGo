from django.shortcuts import render
from productmanagement.models import Category

# Create your views here.
def home_page(request):

    categories = Category.objects.all()

    return render (request, 'index.html',{'categories':categories})