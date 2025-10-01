from django.core import serializers
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from .models import Product
from .forms import ProductForm, RegistrationForm


def show_main(request):
    """List products with navigation to add form and detail pages."""
    products = Product.objects.all()
    context = {
        "app_name": "Football Pro Shop",
        "npm": "2406453530",
        "name": "Muhammad Adra Prakoso",
        "class": "PBP KKI",
        "product_count": products.count(),
        "products": products,
    }
    return render(request, "main.html", context)


@login_required
def add_product(request):
    """Dedicated form page to create a new Product."""
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect("main:show_main")
    else:
        form = ProductForm()

    return render(request, "product_form.html", {"form": form, "app_name": "Football Pro Shop"})


def product_detail(request, id: int):
    """Detail page for a single Product."""
    product = get_object_or_404(Product, pk=id)
    return render(request, "product_detail.html", {"product": product, "app_name": "Football Pro Shop"})


# --- Data serialization endpoints ---
def show_xml(request):
    data = Product.objects.all()
    xml_data = serializers.serialize("xml", data)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    data = Product.objects.all()
    json_data = serializers.serialize("json", data)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, id: int):
    data = Product.objects.filter(pk=id)
    if not data.exists():
        raise Http404("Product not found")
    xml_data = serializers.serialize("xml", data)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json_by_id(request, id: int):
    data = Product.objects.filter(pk=id)
    if not data.exists():
        raise Http404("Product not found")
    json_data = serializers.serialize("json", data)
    return HttpResponse(json_data, content_type="application/json")

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after registration
            return redirect('main:home')  # Redirect to home page
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('main:login')

@login_required
def home(request):
    """Home page showing user details and last login."""
    last_login = request.user.last_login
    
    # Get user's products
    user_products = Product.objects.filter(user=request.user)
    
    context = {
        'username': request.user.username,
        'last_login': last_login,
        'products': user_products,
        'product_count': user_products.count(),
        'app_name': 'Football Pro Shop',
    }
    
    response = render(request, 'home.html', context)
    
    # Set last_login cookie
    if last_login:
        response.set_cookie('last_login', last_login.strftime('%Y-%m-%d %H:%M:%S'))
    
    return response

@login_required
def edit_product(request, id: int):
    """Edit an existing Product."""
    product = get_object_or_404(Product, pk=id, user=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("main:show_main")
    else:
        form = ProductForm(instance=product)

    return render(request, "product_form.html", {"form": form, "app_name": "Football Pro Shop", "is_edit": True})


@login_required
def delete_product(request, id: int):
    """Delete a Product."""
    product = get_object_or_404(Product, pk=id, user=request.user)
    if request.method == "POST":
        product.delete()
        return redirect("main:show_main")
    return render(request, "delete_confirm.html", {"product": product, "app_name": "Football Pro Shop"})