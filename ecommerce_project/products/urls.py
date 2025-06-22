# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Product endpoints
    path('products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Cart endpoints
    path('cart/', views.view_cart, name='view-cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),

    # Order endpoints
    path('orders/', views.user_orders, name='user-orders'),
    path('orders/create/', views.create_order, name='create-order'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),

    # Admin/Staff endpoints
    path('admin/orders/', views.all_orders, name='all-orders'),
    path('admin/orders/<int:order_id>/status/', views.update_order_status, name='update-order-status'),
]