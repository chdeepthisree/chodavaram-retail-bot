

# Register your models here.
from django.contrib import admin
from .models import Product, CustomerLead, ChatLog

admin.site.register(Product)
admin.site.register(CustomerLead)
admin.site.register(ChatLog)
