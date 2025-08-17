from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutPage, name="logout"),

    path('add-new-product/', views.productForm, name="product-form"),

    path('seller-account-<str:pk>', views.sellerAccount, name="seller-account"),

    path('product/', views.product, name="product"),
    path('product-list/', views.productList, name="product-list"),
]