from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('GROCERY', 'Daily Grocery'),
        ('FANCY', 'Fancy & Cosmetics'),
        ('GIFT', 'Gifts & Toys'),
        ('HARDWARE', 'Hardware & Cement'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=15,
        choices=CATEGORY_CHOICES,
        default='GROCERY'
    )
    description = models.TextField(
        help_text="Brand details, size, or tags like wedding/birthday"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"


class CustomerLead(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    needs_human_help = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number


class ChatLog(models.Model):
    customer = models.ForeignKey(
        CustomerLead,
        on_delete=models.CASCADE,
        related_name="conversations"
    )
    sender = models.CharField(
        max_length=10,
        choices=[
            ('USER', 'Customer'),
            ('AI', 'AI Agent'),
            ('HUMAN', 'Shop Owner')
        ]
    )
    message = models.TextField()
    whatsapp_message_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        db_index=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.phone_number} ({self.sender}): {self.message[:30]}"