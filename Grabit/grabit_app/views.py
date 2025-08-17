from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.db.models import Q

User = get_user_model()

def home(request):
    category = Category.objects.all().order_by('c_name')
    context = {'category': category}
    return render(request, "main/home.html", context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else: 
            messages.error(request, 'Email or Password is incorrect')
    
    context = {}
    return render(request, 'main/login.html', context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('f_name')
            last_name = request.POST.get('l_name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                context = {'error_msg': "Passwords don't match. Please try again."}

                return render(request, "main/register.html", context)

            try:
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password1
                )
                login(request, user)
                return redirect('home')
            
            except Exception as e:
                return render(request, "main/register.html", {
                    'error_msg': f"Registration failed: {e}"
                })
        except:
            return redirect('register')

    return render(request, "main/register.html")

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def sellerAccount(request, pk):
    seller_act = StoreAccount.objects.filter(user__id = pk).first()
    product = Product.objects.filter(user = seller_act.user)
    return render(request, "main/seller-account.html", {"seller_act": seller_act, "prodect": product})

@login_required(login_url='login')
def productForm(request):
    if request.method == 'POST':
        try:
            features = request.POST.getlist("feature[]")
            values = request.POST.getlist("value[]")

            desc = dict(zip(features, values))

            product = Product.objects.create(
                user=request.user,
                name=request.POST.get('p_name'),
                price=request.POST.get('price'),
                description=desc,
                discount_percent=request.POST.get('discount'),
                brand=request.POST.get('brand')
            )

            files = request.FILES.getlist('images')
            if not files:
                return render(request, 'main/product-form.html', {
                    "error": "Please upload at least one image"
                })

            for image in files:
                ProductImage.objects.create(product=product, image=image)

            return redirect('home')

        except Exception as e:
            return render(request, 'main/product-form.html', {
                "error": f"Error while adding product: {e}"
            })

    return render(request, 'main/product-form.html')

def productList(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    products = Product.objects.filter(
        Q(name__icontains=q) | 
        Q(description__icontains=q)
    )
    return render(request, "main/product-list.html", {"products": products, "query": q})