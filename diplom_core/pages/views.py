import stripe
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Size, Material, UserProfile, Favorite, ContactMessage, Comments, Cart, CartItem, OrderItem, Order
from django.contrib.auth import login, logout
from .forms import LoginForm, RegisterForm, ContactForm, CommentForm, CheckoutForm
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponse
from django.db import models, transaction
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def index_page(request):
    shop_products = Product.objects.order_by('?')[:2]
    bestsellers = Product.objects.order_by('-purchases_count')[:6]

    context = {
        'shop_products': shop_products,
        'bestsellers': bestsellers
    }

    return render(request, 'index.html', context)


def shop_page(request):
    size_slug = request.GET.get('size')
    material_slug = request.GET.get('material')
    discount_only = request.GET.get('discount_only')
    sort_by = request.GET.get('sort')

    products_list = Product.objects.all()

    if size_slug:
        products_list = products_list.filter(size__slug=size_slug)

    if material_slug:
        products_list = products_list.filter(material__slug=material_slug)

    if discount_only:
        products_list = products_list.filter(discount_percentage__gt=0)


    if sort_by == 'price_asc':
        products_list = products_list.annotate(
            actual_price=models.Case(
                models.When(discount_percentage__gt=0, then='discount_price'),
                default='current_price',
                output_field=models.DecimalField()
            )
        ).order_by('actual_price')

    elif sort_by == 'price_desc':
        products_list = products_list.annotate(
            actual_price=models.Case(
                models.When(discount_percentage__gt=0, then='discount_price'),
                default='current_price',
                output_field=models.DecimalField()
            )
        ).order_by('-actual_price')

    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    all_sizes = Size.objects.all()
    all_materials = Material.objects.all()

    context = {
        'products': products,
        'size': all_sizes,
        'material': all_materials,
        'current_sort': sort_by,
    }
    return render(request, 'shop.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index_path')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user is not None:
                    login(request, user)
                    return redirect('index_path')
            else:
                return redirect('login_path')
        else:
            form = LoginForm()

            context = {
                'title': 'Вход в аккаунт',
                'form': form
            }
            return render(request, 'login.html', context=context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index_path')

    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            profile = UserProfile.objects.create(user=user)
            profile.save()
            return redirect('index_path')
    else:
        form = RegisterForm()

    context = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'register.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('index_path')



def favorite_view(request, pk_products):
    if request.user.is_authenticated:
        user = request.user
        try:
            favorite = Favorite.objects.get(user=user, product_id=pk_products)
            favorite.delete()
            messages.info(request, 'Продукт успешно удалён из избранного.')
        except Favorite.DoesNotExist:
            favorite = Favorite.objects.create(user=user, product_id=pk_products)
            favorite.save()
            messages.success(request, 'Продукт успешно добавлен в избранное.')

        return redirect(request.META.get('HTTP_REFERER', 'index_path'))
    else:
        return redirect('login_path')


def favorite_path(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)
        context = {
            'title': 'Избранное',
            'favorites': favorites,
        }
        return render(request, 'favorites.html', context=context)
    else:
        return redirect('login_path')

def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )

            return redirect('index_path')
    else:
        form = ContactForm()

    context = {
        'form': form
    }
    return render(request, 'contacts.html', context)


def detail_page(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    comments = Comments.objects.filter(product=product).order_by('-created_date')

    if request.user.is_authenticated:
        form = CommentForm()
    else:
        form = None

    context = {
        'product': product,
        'comments': comments,
        'form': form,
    }
    return render(request, 'detail.html', context)

@login_required
def add_comment(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)

    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен.')

    return redirect('detail_path', product_slug=product.slug)


@login_required
def delete_comment(request, pk):
    try:
        comment = Comments.objects.get(pk=pk)
    except Comments.DoesNotExist:
        raise Http404("Комментарий не найден")
    if request.user.is_superuser or request.user == comment.user:
        comment.delete()
        messages.info(request, 'Комментарий успешно удалён.')
    else:
        messages.error(request, 'У вас нет прав для удаления этого комментария.')

    return redirect(request.META.get('HTTP_REFERER', 'detail_path'))

def cart_add(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login_path')

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if OrderItem.objects.filter(order__user=request.user, order__paid=True, product=product).exists():
        messages.info(request, f'Вы уже приобрели этот товар.')
        return redirect(request.META.get('HTTP_REFERER', 'shop_path'))

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if item_created:
        messages.success(request, f'Товар "{product.name}" успешно добавлен в корзину.')
    else:
        messages.info(request, f'Товар "{product.name}" уже находится в корзине.')

    return redirect(request.META.get('HTTP_REFERER', 'shop_path'))


def cart_remove(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login_path')

    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.info(request, f'Товар "{product_name}" был успешно удален из корзины.')
    except CartItem.DoesNotExist:
        messages.error(request, 'Этого товара нет в вашей корзине.')

    return redirect('cart_detail_path')

@login_required
def cart_detail(request):
    cart = None
    total_price = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_price = sum(item.get_total_price() for item in cart.items.all())
        except Cart.DoesNotExist:
            pass

    context = {
        'cart': cart,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

stripe.api_key = settings.STRIPE_PUBLIC_KEY

def checkout_page(request):
    cart = None
    total_price = 0
    form = CheckoutForm()

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_price = sum(item.get_total_price() for item in cart.items.all())
        except Cart.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    shipping_address=form.cleaned_data['shipping_address'],
                    phone_number=form.cleaned_data['phone_number'],
                )

                line_items = []
                for item in cart.items.all():
                    price = item.product.get_actual_price()
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=price,
                        quantity=item.quantity
                    )
                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': item.product.name,
                            },
                            'unit_amount': int(price * 100),
                        },
                        'quantity': item.quantity,
                    })

                try:
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=request.build_absolute_uri(reverse_lazy('success_path')),
                        cancel_url=request.build_absolute_uri(reverse_lazy('cancel_path')),
                        metadata={'order_id': order.id}
                    )
                    return redirect(checkout_session.url, code=303)
                except Exception as e:
                    messages.error(request, f'Произошла ошибка при создании сессии Stripe: {e}')
                    return redirect('checkout_path')

    context = {
        'cart': cart,
        'total_price': total_price,
        'form': form
    }
    return render(request, 'checkout.html', context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            with transaction.atomic():
                try:
                    order = Order.objects.get(id=order_id)
                    order.paid = True
                    order.save()

                    for item in order.items.all():
                        item.product.purchases_count += item.quantity
                        item.product.save()

                    try:
                        cart = Cart.objects.get(user=order.user)
                        cart.items.all().delete()
                        print(f"Корзина пользователя {order.user.username} успешно очищена.")
                    except Cart.DoesNotExist:
                        print(f"Корзина пользователя {order.user.username} не найдена.")

                except Order.DoesNotExist:
                    print(f"Заказ с ID {order_id} не найден.")

    return HttpResponse(status=200)

def success_page(request):
    if request.user.is_authenticated:
        try:
            order = Order.objects.filter(user=request.user, paid=False).order_by('-created_at').first()

            if order:
                with transaction.atomic():
                    order.paid = True
                    order.save()

                    for item in order.items.all():
                        item.product.purchases_count += item.quantity
                        item.product.save()

                    try:
                        cart = Cart.objects.get(user=request.user)
                        cart.items.all().delete()
                        print(f"Корзина пользователя {request.user.username} успешно очищена.")
                    except Cart.DoesNotExist:
                        print(f"Корзина пользователя {request.user.username} не найдена.")

                    print(f"Заказ {order.id} успешно обработан на success_page.")
            else:
                print("Неоплаченный заказ не найден для текущего пользователя.")

        except Exception as e:
            print(f"Произошла ошибка при обработке успешной оплаты: {e}")

    return render(request, 'success.html')

def cancel_page(request):
    return render(request, 'cancel.html')


@login_required
def purchases_page(request):
    user_orders = Order.objects.filter(user=request.user, paid=True).order_by('-created_at')

    context = {
        'user_orders': user_orders
    }
    return render(request, 'purchases.html', context)