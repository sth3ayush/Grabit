from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=10)
    dob = models.DateField()
    default_address = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(0)]
        )
    description = models.TextField(null=True, blank=True)
    discount_percent = models.DecimalField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        decimal_places=1,
        max_digits=4,
        default=0.0
        )
    brand = models.CharField(max_length=100, default="No Brand")

    #Calculate the average rating of product
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            avg = sum(r.rating for r in ratings) / ratings.count()
            return round(avg)
        return 0

    #Create a dynamic description incase description not given
    def save(self, *args, **kwargs):
        if not self.description:
            self.description = f"{self.name} at {self.price}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class ProductQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.question[:15]}..."
    
class ProductRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ratings')
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
        return f"{self.user.username} rated {self.product.name} - {self.rating}"