from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from django.urls import reverse

User = get_user_model()

def home(request):
    category = Category.objects.all().order_by('c_name')
    discount_deals = Product.objects.all().order_by('discount_percent')[:5]
    latest_deals = Product.objects.all().order_by('created_at')[:5]

    context = {'discount_deals': discount_deals, 'latest_deals': latest_deals, 'category': category}
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
            messages.success(request, 'Login Successful!')
            return redirect('home')
        else: 
            messages.error(request, 'Email or Password is incorrect! Please try again.')
    
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
                messages.error(request, "Passwords don't match! Please try again.")

                return render(request, "main/register.html")

            try:
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password1
                )
                login(request, user)
                messages.success(request, "Account created successfully.")
                return redirect('home')
            
            except Exception as e:
                messages.error(request, "Registration failed: {e}")
                return render(request, "main/register.html")
        except Exception as e:
            messages.error(request, "Error: {e}")
            return redirect('register')

    return render(request, "main/register.html")

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    messages.info(request, "Logged out.")
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
            discount_percent = Decimal(request.POST.get('discount') or 0)
            price = Decimal(request.POST.get('price') or 0)

            if discount_percent > 0:
                old_price = price
                discount_amt = (old_price * discount_percent) / Decimal(100)
                price = old_price - discount_amt
            else:
                old_price = price

            features = request.POST.getlist("feature[]")
            values = request.POST.getlist("value[]")

            desc = dict(zip(features, values))

            product = Product.objects.create(
                user=request.user,
                name=request.POST.get('p_name'),
                price = price,
                old_price = old_price,
                description=desc,
                discount_percent = discount_percent,
                brand=request.POST.get('brand')
            )

            files = request.FILES.getlist('images')
            if not files:
                messages.warning(request, "Upload at least 1 image")
                return render(request, 'main/product-form.html')

            for image in files:
                ProductImage.objects.create(product=product, image=image)
            messages.success(request, "Product added successfully.")
            return redirect('home')

        except Exception as e:
            messages.error(request, "Error while adding product: {e}")
            return render(request, 'main/product-form.html')

    return render(request, 'main/product-form.html')

def product(request, pk):
    product = Product.objects.get(id=pk)
    product_imgs = ProductImage.objects.filter(product=product)
    store = StoreAccount.objects.get(user = product.user)
    questions = ProductQuestion.objects.filter(product = product)
    
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                ProductQuestion.objects.create(
                    user = request.user,
                    product = product,
                    question = request.POST.get('question')
                )
            except Exception as e:
                messages.error(request, "Error while adding question: {e}")
                return render(request, "main/product.html")
        else:
            messages.error(request, "You must be logged in to ask a question.")
            return redirect('login')
        return redirect(reverse("product", args=[pk]))
    context = {'product': product, 'product_imgs': product_imgs, 'store': store, 'questions': questions}
    return render(request, "main/product.html", context)

def productList(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    products = Product.objects.filter(
        Q(name__icontains=q) | 
        Q(description__icontains=q)
    )
    return render(request, "main/product-list.html", {"products": products, "query": q})