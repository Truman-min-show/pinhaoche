from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

#用户表
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=100, blank=True)
    user_type = models.CharField(max_length=10, choices=[('passenger', 'Passenger'), ('driver', 'Driver')], default='passenger')
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('banned', 'Banned')], default='active')
    register_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

#司机信息表
class Driver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    approval_status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    rating = models.FloatField(default=5.0)

#车辆信息表
class Vehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20, unique=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    seats = models.IntegerField()

#地点信息表
class Location(models.Model):
    name = models.CharField(max_length=255)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    address_detail = models.TextField(blank=True, null=True)


#拼车订单表
class CarpoolOrder(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='start_orders')
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='end_orders')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#乘客需求表
class PassengerRequest(models.Model):
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='origin_requests')
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='destination_requests')
    departure_time = models.DateTimeField()
    seats_needed = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#司机发布信息表
class DriverOffer(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    route = models.JSONField()  # 存储路线信息，可以是多个地点的列表
    departure_time = models.DateTimeField()
    available_seats = models.IntegerField()
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
#匹配记录表
class MatchRecord(models.Model):
    request = models.ForeignKey(PassengerRequest, on_delete=models.CASCADE)
    offer = models.ForeignKey(DriverOffer, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('matched', 'Matched'),
        ('cancelled', 'Cancelled')
    ], default='matched')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#支付管理表
class Payment(models.Model):
    order = models.ForeignKey(CarpoolOrder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#评价反馈表
class Review(models.Model):
    order = models.ForeignKey(CarpoolOrder, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)