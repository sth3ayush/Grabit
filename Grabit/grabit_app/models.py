from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    is_seller = models.BooleanField(default=False)
    mobile_no = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    default_address = models.CharField(max_length=300, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(0)]
        )
    description = models.JSONField(null=True, blank=True)
    discount_percent = models.DecimalField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        decimal_places=1,
        max_digits=4,
        default=0.0
        )
    brand = models.CharField(max_length=100, default="No Brand")

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            avg = sum(r.rating for r in ratings) / ratings.count()
            return round(avg, 1)
        return 0

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = f"{self.name} at {self.price}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} {self.name}"
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Product_images')

    def __str__(self):
        return f"{self.product.name} - {self.image.name}"
    
class ProductQuestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} {self.question[:10]}..."
    
class ProductRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    #Limit one user to rate a product only once
    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'product'], name='unique_user_product_rating')
        ]

    def __str__(self):
        return f"{self.user.email} rated {self.product.name} - {self.rating}"
    
class Category(models.Model):
    c_name = models.CharField(max_length=77, unique=True)

    def __str__(self):
        return self.c_name
    
class StoreAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100, unique=True)
    store_logo = models.ImageField(upload_to="Store_logo", null=True, blank=True)
    store_verification = models.ImageField(upload_to="Store", null=True, blank=True)

    contact_no = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name
    
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=1
    )

    def __str__(self):
        return f"{self.user.email} {self.product.name[:10]}..."