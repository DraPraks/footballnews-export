from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.show_main, name='show_main'),
    # HTML pages
    path('add/', views.add_product, name='add_product'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    # Data endpoints
    path('xml/', views.show_xml, name='show_xml'),
    path('json/', views.show_json, name='show_json'),
    path('xml/<int:id>/', views.show_xml_by_id, name='show_xml_by_id'),
    path('json/<int:id>/', views.show_json_by_id, name='show_json_by_id'),
]