from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('order/<int:table_id>/', views.order_items, name='order_items'),
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('saved-orders/', views.saved_orders, name='saved_orders'),
    path('download-orders-csv/', views.download_orders_csv, name='download_orders_csv'),
    path('delete-orders/', views.delete_orders, name='delete_orders'),

    

    
]
