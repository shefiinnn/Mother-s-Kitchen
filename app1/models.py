from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

class reg_form_us(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    image = models.FileField(upload_to='file')
    address=models.CharField(max_length=100,default="xxx")
    location=models.CharField(max_length=50,default="Kochi")

class reg_form_ch(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    image = models.FileField(upload_to='file')
    id_card = models.FileField(upload_to='file')  # Changed from id to id_card
    location = models.CharField(max_length=100)
    address = models.CharField(max_length=50)
    accnum = models.BigIntegerField()
    ifsc = models.CharField(max_length=50)
    food_posts = GenericRelation('foodpost', related_query_name='chef_posts')
    reviews = GenericRelation('Review', related_query_name='chef_reviews')

class login(models.Model):
    username = models.CharField(max_length=100, unique=True)
    passw = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    uid = GenericForeignKey('content_type', 'object_id')
    utype = models.CharField(max_length=50, choices=[('user', 'User'), ('chef', 'Chef'),('admin','Admin')])
class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class foodpost(models.Model): 
    title = models.CharField(max_length=100)
    desc = models.TextField()  
    image = models.ImageField(upload_to='file') 
    image1 = models.ImageField(upload_to='file',default='file/button.png')
    image2 = models.ImageField(upload_to='file',default='file/ealogo.jpg')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    location = models.CharField(max_length=150)  # Store Address
    latitude = models.FloatField(default=0.0)  # Store Latitude
    longitude = models.FloatField(default=0.0)  # Store Longitude
    dining_type = models.CharField(max_length=50, default="Dine-in") 
    category=models.CharField(max_length=50,default="Lunch")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,default=1)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    chef = GenericForeignKey('content_type', 'object_id')  # Link to the chef

    def __str__(self):
        return self.title



from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(reg_form_us, on_delete=models.CASCADE)  # Linking to user model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Generic FK for chefs
    object_id = models.PositiveIntegerField()
    chef = GenericForeignKey('content_type', 'object_id')  # Link to the chef
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Star rating (1-5)
    comment = models.TextField(blank=True, null=True)  # Optional comment
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.user.name} - {self.chef.name} ({self.rating} stars)"

    
class Orders(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    user = models.ForeignKey("reg_form_us", on_delete=models.CASCADE)
    food = models.ForeignKey("foodpost", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    chef = models.ForeignKey("reg_form_ch", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    payment_status = models.BooleanField(default=False)  # False means unpaid, True means paid
    razorpay_order_id = models.CharField(max_length=100,unique=True, blank=True, null=True)  # Store Razorpay order ID
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)  # Store Razorpay payment ID
    razorpay_payment_signature = models.CharField(max_length=100, blank=True, null=True)  # Payment signature

    def __str__(self):
        return f"Order {self.id} - {self.user.name}"
class Report(models.Model):
    user = models.ForeignKey(reg_form_us, on_delete=models.CASCADE)
    chef = models.ForeignKey(reg_form_ch, on_delete=models.CASCADE)
    food = models.ForeignKey(foodpost, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.name} on {self.chef.name}"