from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Size, Material, Product, GalleryProducts, ContactMessage, Order, OrderItem


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['pk']
    list_per_page = 5

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['pk']
    list_per_page = 5



class ProductGalleryInline(admin.TabularInline):
    model = GalleryProducts
    extra = 1


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'current_price', 'discount_percentage']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['size', 'material']
    inlines = [ProductGalleryInline]
    ordering = ['pk']

    def save_model(self, request, obj, form, change):
        if obj.current_price and obj.discount_percentage > 0:
            result = round(float(obj.current_price) * (1 - obj.discount_percentage / 100))
            obj.discount_price = result
        super().save_model(request, obj, form, change)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    list_display_links = ['name', 'email']
    search_fields = ['name', 'email', 'message']
    list_per_page = 10
    readonly_fields = ['name', 'email', 'message', 'created_at']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'full_name', 'email', 'created_at', 'paid']
    list_filter = ['paid', 'created_at']
    search_fields = ['full_name', 'email', 'phone_number']
    readonly_fields = ['created_at']
    inlines = [OrderItemInline]
