from django.core import serializers
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm


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


def add_product(request):
    """Dedicated form page to create a new Product."""
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
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