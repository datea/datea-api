from django.contrib import admin
from category.models import Category

class CategoryAdmin(admin.ModelAdmin):
    model = Category

admin.site.register(Category, CategoryAdmin)
