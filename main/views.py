from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm


def show_main(request):
    # Handle product creation without admin access
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main:show_main")
    else:
        form = ProductForm()

    products = Product.objects.all()
    context = {
        "app_name": "Football Pro Shop",
        "npm": "2406453530",
        "name": "Muhammad Adra Prakoso",
        "class": "PBP KKI",
        "product_count": products.count(),
        "products": products,
        "form": form,
    }
    return render(request, "main.html", context)