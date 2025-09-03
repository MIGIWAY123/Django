from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index_path'),
    path('shop/', views.shop_page, name='shop_path'),
    path('user/login/', views.login_view, name='login_path'),
    path('user/register/', views.register_view, name='register_path'),
    path('user/logout/', views.logout_view, name='logout_path'),
    path('favorites/', views.favorite_path, name='favorite_path'),
    path('favorite/<int:pk_products>/', views.favorite_view, name='favorite_add_path'),
    path('about/', views.about_page, name='about_path'),
    path('contacts/', views.contact_page, name='contacts_path'),
    path('product/<slug:product_slug>/', views.detail_page, name='detail_path'),
    path('save/comment/<int:product_pk>/', views.add_comment, name='save_comment_active'),
    path('delete/comment/<int:pk>/', views.delete_comment, name='delete_comment_active'),
    path('cart/', views.cart_detail, name='cart_detail_path'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout_page, name='checkout_path'),
    path('success/', views.success_page, name='success_path'),
    path('cancel/', views.cancel_page, name='cancel_path'),
    path('purchases/', views.purchases_page, name='purchases_path'),
]