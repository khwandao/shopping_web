"""shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from xml.dom.minidom import Document
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from shopping_web import views

urlpatterns = [
    
    path('admin/', admin.site.urls),    
    path('payment', views.payment, name='payment'),
    path('logout', views.custom_logout, name='logout'),
    path('',views.index, name='/'),
    
    path('product-detail', views.product_detail, name='product-detail'),
    path('product-detail/<int:pid>/', views.product_detail, name='product-detail'),

    path('contact', views.contact, name='contact'),
    path('search', views.search, name='search'),
    path('cart', views.cart, name='cart'),
    path('login', views.userLogin, name='login'),
    path('register', views.register, name='register'),
    path('shoes', views.shoes, name='shoes'),
    path('bags', views.bags, name='bags'),
    path('add-to-cart', views.add_to_cart, name='add-to-cart'),
    path('delete-item-from-cart', views.delete_item_from_cart, name='delete-item-from-cart'),
    path('refresh-cart', views.refresh_cart, name='refresh-cart'),
    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

