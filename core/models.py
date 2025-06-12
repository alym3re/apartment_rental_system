from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    CLIENT = 1
    TENANT = 2
    ADMIN = 3
    
    ROLE_CHOICES = (
        (CLIENT, 'Client'),
        (TENANT, 'Tenant'),
        (ADMIN, 'Admin'),
    )
    
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=CLIENT)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    facebook_account = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username

class Unit(models.Model):
    AVAILABLE = 1
    OCCUPIED = 2
    STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (OCCUPIED, 'Occupied'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    payment_inclusions = models.TextField()
    house_rules = models.TextField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=AVAILABLE)
    main_image = models.ImageField(upload_to='units/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UnitImage(models.Model):
    unit = models.ForeignKey(Unit, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='units/')
    caption = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.unit.name}"

class Application(models.Model):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    facebook_account = models.URLField(blank=True, null=True)
    occupation = models.CharField(max_length=100)
    number_of_people = models.PositiveIntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    applied_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Application by {self.full_name} for {self.unit.name}"

class Lease(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lease for {self.tenant.username} at {self.unit.name}"

class Payment(models.Model):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )
    
    CASH = 1
    GCASH = 2
    BANK_TRANSFER = 3
    CHECK = 4
    CREDIT_CARD = 5
    
    PAYMENT_MODE_CHOICES = (
        (CASH, 'Cash'),
        (GCASH, 'GCash'),
        (BANK_TRANSFER, 'Bank Transfer'),
        (CHECK, 'Check'),
        (CREDIT_CARD, 'Credit Card'),
    )
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    mode_of_payment = models.PositiveSmallIntegerField(
        choices=PAYMENT_MODE_CHOICES,
        default=CASH
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.lease}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_global = models.BooleanField(default=True)
    recipients = models.ManyToManyField(User, related_name='announcements', blank=True)

    def __str__(self):
        return self.title

class Conversation(models.Model):
    subject = models.CharField(max_length=200)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject or f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"

class LeaveRequest(models.Model):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )
    
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
    reason = models.TextField()
    requested_end_date = models.DateField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Leave request by {self.tenant.username}"