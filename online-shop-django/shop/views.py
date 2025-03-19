from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from shop.models import Product, Category
from cart.forms import QuantityForm


def paginat(request, list_objects):
    """Paginator function"""
    p = Paginator(list_objects, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return page_obj

def home_page(request):
    max_price = request.GET.get('max_price', None)  # URL-dan max_price olish
    products = Product.objects.all()  # Barcha mahsulotlarni olish

    if max_price:
        try:
            max_price = float(max_price)  # max_price raqam ekanligini tekshirish
            products = products.filter(price__lte=max_price)  # Narx bo‘yicha filter
        except ValueError:
            pass  # Agar noto‘g‘ri qiymat bo‘lsa, filter ishlamaydi

    paginator = Paginator(products, 6)  # 6 tadan mahsulot chiqarish
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)  # Sahifalashni qo‘llash

    context = {'products': products_page}
    return render(request, 'home_page.html', context)

def product_detail(request, slug):
    """Product detail page"""
    form = QuantityForm()
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    related_products = Product.objects.filter(category=product.category)[:5]

    context = {
        'title': product.title,
        'product': product,
        'form': form,
        'favorites': 'favorites',
        'related_products': related_products
    }
    if request.user.is_authenticated:
        if request.user.likes.filter(id=product.id).exists():
            context['favorites'] = 'remove'

    return render(request, 'product_detail.html', context)


@login_required
def add_to_favorites(request, product_id):
    """Add product to favorites"""
    product = get_object_or_404(Product, id=product_id)
    request.user.likes.add(product)
    return redirect('shop:product_detail', slug=product.slug)


@login_required
def remove_from_favorites(request, product_id):
    """Remove product from favorites"""
    product = get_object_or_404(Product, id=product_id)
    request.user.likes.remove(product)
    return redirect('shop:favorites')


@login_required
def favorites(request):
    """Display user's favorite products"""
    products = request.user.likes.all()
    context = {'title': 'Favorites', 'products': products}
    return render(request, 'favorites.html', context)


def search(request):
    """Search products by title"""
    query = request.GET.get('q')
    products = Product.objects.filter(title__icontains=query)
    context = {'products': paginat(request, products)}
    return render(request, 'home_page.html', context)


def filter_by_category(request, slug):
    """Show products for a category and its subcategories"""
    category = get_object_or_404(Category, slug=slug)
    sub_categories = category.sub_categories.all()

    all_categories = [category] + list(sub_categories)
    products = Product.objects.filter(category__in=all_categories).select_related('category')

    context = {'products': paginat(request, products)}
    return render(request, 'home_page.html', context)
