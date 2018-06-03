from django.db import models
from django.contrib.auth.models import User
import time
import os
import uuid
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from main_app.models import Profil
from ckeditor.fields import RichTextField


# For rename the file before save
@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        # eg: filename = 'my uploaded file.jpg'
        ext = filename.split('.')[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        # eg: 'my-uploaded-file'
        new_name = '-'.join(filename.replace('.%s' % ext, '').split())

        # eg: 'my-uploaded-file_64c942aa64.jpg'
        renamed_filename = '%(new_name)s_%(uid)s.%(ext)s' % {'new_name': new_name, 'uid': uid, 'ext': ext}

        # eg: 'images/2017/01/29/my-uploaded-file_64c942aa64.jpg'
        return os.path.join(self.path, renamed_filename)


class Address(models.Model):
    company = models.CharField(max_length=254, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=254)
    post_code = models.CharField(max_length=254)
    country = models.CharField(max_length=254)
    region = models.CharField(max_length=254)


class CommerceCategory(models.Model):
    name = models.CharField(max_length=200)
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))

    def __str__(self):
        return self.name


class CommerceSCategoryOne(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(CommerceCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CommerceSCategoryTwo(models.Model):
    name = models.CharField(max_length=200)
    category_one = models.ForeignKey(CommerceSCategoryOne, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CommerceSCategory(models.Model):
    name = models.CharField(max_length=200)
    category_two = models.ForeignKey(CommerceSCategoryTwo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=200)
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path), blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=200)
    image_path = time.strftime('images/%Y/%m/%d')
    image_profile = models.ImageField(upload_to=PathAndRename(image_path))
    image_cover = models.ImageField(upload_to=PathAndRename(image_path))
    description = models.TextField(null=True, blank=True)
    number_visitors = models.IntegerField(default=0)
    date_creation = models.DateField(auto_now_add=True)
    owner = models.OneToOneField(Profil, null=False, on_delete=models.CASCADE)
    address = models.CharField(max_length=300, null=True, blank=True)
    tel = models.CharField(max_length=30, null=True)
    approved = models.BooleanField(default=False)
    categories = models.ManyToManyField(CommerceSCategoryOne, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))
    date_add = models.DateField(auto_now_add=True)
    cat = models.ForeignKey(CommerceSCategory, on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True)
    accessories = models.ManyToManyField("self", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    number_views = models.IntegerField(default=0, null=False, blank=False, editable=True)
    quantity_min = models.IntegerField(default=1, null=True, blank=True)
    unit = models.CharField(max_length=200, default='Piece')
    is_pro = models.BooleanField(default=False)
    supplier = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    packaging_detail = models.CharField(max_length=1000, null=True, blank=True)
    delivery_time = models.CharField(max_length=1000, null=True, blank=True)
    content = RichTextField(default=' ')
    price_from = models.BooleanField(default=False)
    old_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CommerceInformation(models.Model):
    name = models.CharField(max_length=250, default="detail")
    value = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return 'info {0} {1}'.format(str(self.pk), self.product.name)


class CommerceImage(models.Model):
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return 'image {0} {1}'.format(str(self.pk), self.product.name)


class CommerceRatting(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254),
    date_add = models.DateField(auto_now_add=True, editable=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return "vote {0},  {1} : {2}".format(str(self.pk), str(self.value), self.product.name)


class Color(models.Model):
    name = models.CharField(max_length=200)
    code_hex = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Stock(models.Model):
    quantity = models.IntegerField(default=0)
    first_quantity = models.IntegerField(default=0)
    price_sup = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return '{0} de {1} {2}'.format(str(self.quantity), self.product.name, self.color.name)
    
    def new_price(self):
        return self.product.price + self.price_sup
    
    def percent(self):
        return (self.quantity * 100) / self.first_quantity
    
    def sold(self):
        return self.first_quantity - self.quantity


class Specification(models.Model):
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=1000)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ' ' + self.product.name


class Sale(models.Model):
    percentage = models.IntegerField()
    date_end = models.DateTimeField(blank=False, default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_daily = models.BooleanField(default=False)

    def __str__(self):
        return str(self.percentage) + "% for " + self.product.name
    
    def new_price(self):
        return self.product.price - ((self.product.price*self.percentage)/100) 


class WishList(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.user.username + ' ' + self.product.name


class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return '{0} {1} de {2}'.format(str(self.quantity), self.product.name, self.user.user.username)


payment_method = (('Cash On Delivery', 'Cash On Delivery'), ('Paypal', 'Paypal'))
delivery_method = (('Free Shipping', 'Free Shipping'), ('Flat Shipping Rate', 'Flat Shipping Rate'))


class Order(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=200, default="Created")
    payment_method = models.CharField(max_length=20, choices=payment_method, default='Cash On Delivery')
    delivery_method = models.CharField(max_length=20, choices=delivery_method, default='Free Shipping')
    comment = models.TextField(null=False, blank=True, default="")
    track_number = models.CharField(max_length=300, null=True, blank=True)
    date_payment = models.DateField(null=True, blank=True)
    date_complete = models.DateField(null=True, blank=True)
    user = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return 'Order {0} de {1}'.format(str(self.pk), self.user.user.username)


class OrderLine(models.Model):
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=15, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    def price_unit(self):
        return self.total / self.quantity


class Slide(models.Model):
    image_path = time.strftime('slides/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_add = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)


class ShippingAddress(Address):
    user = models.OneToOneField(Profil, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} {1}'.format(self.user.user.username, self.address)


class BillingAddress(Address):
    user = models.OneToOneField(Profil, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} {1}'.format(self.user.user.username, self.address)


class Mailing(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    date_add = models.DateField(auto_now_add=True)

    def __str__(self):
        return "{} is {}".format(self.email, self.active)


class Message(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    date_add = models.DateField(auto_now_add=True)

    def __str__(self):
        return "{} said '{}...'".format(self.name, self.message[:200])


class Description(models.Model):
    text = models.TextField()
    product = models.OneToOneField(Product, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return "{} : {}".format(self.product.name, self.text[:200])


class Compare(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.user.username + ' ' + self.product.name


class MessageSupplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    tel = models.CharField(max_length=200)
    message = models.TextField()
    date_add = models.DateField(auto_now_add=True)
    supplier = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return "{} said '{}...'".format(self.name, self.message[:200])
