from django.shortcuts import render
from .models import *

def home(request):
    category = Category.objects.all().order_by('c_name')
    context = {'category': category}
    return render(request, "main/home.html", context)