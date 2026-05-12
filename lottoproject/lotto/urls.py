from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('purchase/auto/', views.purchase_auto, name='purchase_auto'),
    path('purchase/manual/', views.purchase_manual, name='purchase_manual'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('results/', views.check_results, name='check_results'),

    path('manager/', views.admin_dashboard, name='admin_dashboard'),
    path('manager/sales/', views.admin_sales, name='admin_sales'),
    path('manager/draw/', views.admin_draw, name='admin_draw'),
    path('manager/draw/<int:round_number>/', views.admin_draw_result, name='admin_draw_result'),
    path('manager/winners/', views.admin_winners, name='admin_winners'),
]
