import json
from datetime import datetime

from django.core import serializers
from django.http import Http404, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.html import strip_tags
import requests

from .models import Product
from .forms import ProductForm, RegistrationForm


def _load_json(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _make_querydict(payload: dict | None) -> QueryDict:
    qd = QueryDict(mutable=True)
    if not payload:
        return qd
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                qd.setlistdefault(key, []).append("on")
            continue
        if isinstance(value, (list, tuple)):
            qd.setlist(key, ["" if item is None else str(item) for item in value])
        else:
            qd[key] = str(value)
    return qd


def _serialize_product(product: Product, user) -> dict:
    owner_id = product.user_id
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "thumbnail": product.thumbnail,
        "category": product.category,
        "category_display": product.get_category_display(),
        "is_featured": product.is_featured,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "owner": product.user.username if product.user_id else None,
        "can_edit": bool(getattr(user, "is_authenticated", False) and owner_id == user.id),
    }


@ensure_csrf_cookie
def show_main(request):
    """List products with navigation to add form and detail pages."""
    context = {
        "app_name": "Football Pro Shop",
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
    # Filter products by authenticated user if requested
    if request.user.is_authenticated and request.GET.get('user_only') == 'true':
        data = Product.objects.filter(user=request.user)
    else:
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

@ensure_csrf_cookie
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

@ensure_csrf_cookie
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

# AJAX helpers for CRUD operations

@require_http_methods(["GET", "POST"])
def api_products(request):
    """Return product list or create a new product via AJAX."""
    if request.method == "GET":
        products = Product.objects.all()
        data = [_serialize_product(product, request.user) for product in products]
        return JsonResponse({"products": data})

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    payload = _load_json(request) if request.content_type == "application/json" else request.POST.dict()
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    form = ProductForm(_make_querydict(payload))
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    product = form.save(commit=False)
    product.user = request.user
    product.save()
    return JsonResponse({"product": _serialize_product(product, request.user)}, status=201)


@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def api_product_detail(request, id: int):
    product = get_object_or_404(Product, pk=id)

    if request.method == "GET":
        return JsonResponse({"product": _serialize_product(product, request.user)})

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if product.user_id != request.user.id:
        return JsonResponse({"error": "You do not have permission for this product."}, status=403)

    if request.method in {"PUT", "PATCH"}:
        payload = _load_json(request)
        if payload is None:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        form = ProductForm(_make_querydict(payload), instance=product)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        product = form.save()
        return JsonResponse({"product": _serialize_product(product, request.user)})

    product.delete()
    return JsonResponse({"deleted": True, "id": id}, status=200)


@require_http_methods(["POST"])
def api_login(request):
    payload = _load_json(request) if request.content_type == "application/json" else request.POST.dict()
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    form = AuthenticationForm(request, data=payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    user = form.get_user()
    login(request, user)
    return JsonResponse({
        "success": True,
        "redirect": reverse("main:home"),
    })


@require_http_methods(["POST"])
def api_register(request):
    payload = _load_json(request) if request.content_type == "application/json" else request.POST.dict()
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    form = RegistrationForm(_make_querydict(payload))
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    user = form.save()
    login(request, user)
    return JsonResponse({
        "success": True,
        "redirect": reverse("main:home"),
    }, status=201)


@login_required
@require_http_methods(["POST"])
def api_logout(request):
    logout(request)
    return JsonResponse({"success": True, "redirect": reverse("main:login")})


def proxy_image(request):
    """Proxy endpoint to handle CORS-safe image loading from external sources."""
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)


@csrf_exempt
def create_product_flutter(request):
    """Handle product creation from Flutter with JSON payload."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
        
        data = json.loads(request.body)
        title = strip_tags(data.get("name", ""))
        description = strip_tags(data.get("description", ""))
        price = data.get("price", 0)
        thumbnail = data.get("thumbnail", "")
        category = data.get("category", "")
        is_featured = data.get("is_featured", False)
        
        try:
            product = Product.objects.create(
                name=title,
                description=description,
                price=price,
                thumbnail=thumbnail,
                category=category,
                is_featured=is_featured,
                user=request.user
            )
            return JsonResponse({
                "status": "success",
                "message": "Product created successfully!",
                "product_id": product.id
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Failed to create product: {str(e)}"
            }, status=400)
    else:
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method."
        }, status=405)