from django.contrib import admin
from .models import Product,Cart,Message,Profile

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Message)
admin.site.register(Profile)