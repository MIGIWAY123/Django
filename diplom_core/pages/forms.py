from django import forms
from .models import Product, Size, Material, UserProfile, Favorite, Comments, ContactMessage, Cart, CartItem, Order
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={
        'placeholder': 'Login'
    }))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'placeholder': 'Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'password']

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={
        'placeholder': 'Login'
    }))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class ContactForm(forms.Form):
    name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'required': True,
            'class': 'form-input'
        })
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'required': True,
            'class': 'form-input'
        })
    )
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'placeholder': 'Your Message',
            'required': True,
            'rows': 5,
            'class': 'form-textarea'
        })
    )

class CommentForm(forms.ModelForm):
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        'rows': 4,
        'placeholder': 'Your Comment',
        'class': 'comment-form-textarea'
    }))
    class Meta:
        model = Comments
        fields = ['text']

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'shipping_address', 'phone_number']
        labels = {
            'full_name': '',
            'email': '',
            'shipping_address': '',
            'phone_number': '',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'required': True}),
            'shipping_address': forms.TextInput(attrs={'placeholder': 'Shipping Address', 'required': True}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number', 'required': True}),
        }