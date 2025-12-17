from django.urls import path
from . import views

urlpatterns = [
    path("passengers/", views.passenger_list, name="passenger_list"),
    path("passengers/<int:id>/", views.passenger_detail, name="passenger_detail"),
    path("passengers/add/", views.passenger_add, name="passenger_add"),
    path("passengers/<int:id>/edit/", views.passenger_edit, name="passenger_edit"),
    path("passengers/<int:id>/delete/", views.passenger_delete, name="passenger_delete"),
    path("clients/", views.client_listapi, name="client_list"),
    path("client/<int:client_id>/", views.client_detail_api, name="client_detail"),
    path("clients/<int:pk>/delete/", views.delete_client_api, name="delete_client_api"),
    path("items/", views.items_listapi, name = "items_list"),
    path("items/<int:pk>/delete/", views.delete_item_api, name = "delete_item_api"),
    path("items/<int:item_id>/", views.item_detail_api, name = "item<int:item_id"),
]
