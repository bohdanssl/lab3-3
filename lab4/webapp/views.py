from django.shortcuts import render, redirect, get_object_or_404
from main.models import Passenger
from .forms import PassengerForm
from .NetworkHelper import NetworkHelper
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse

api = NetworkHelper("http://localhost:8001/", token="0d064f5cb42e416a6de2e051ae5b04b352cdb5c3")

def client_listapi(request):
    clients = api.get_clients()
    return render(request, "webapp/clients_list.html", {"clients": clients})

def items_listapi(request):
    items = api.get_items()
    return render(request, "webapp/items_list.html", {"items": items})

def delete_client_api(request, pk):
    if request.method == "POST":
        api.delete_client(pk)
    return redirect("clients_list")

def delete_item_api(request, pk):
    if request.method == "POST":
        api.delete_item(pk)
    return redirect("items_list")


def client_detail_api(request, client_id):
    try:
        item_data = api.get_client_by_id(client_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return JsonResponse({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
        elif e.response.status_code == 401:
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(item_data)

def item_detail_api(request, item_id):
    try:
        item_data = api.get_item_by_id(item_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return JsonResponse({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        elif e.response.status_code == 401:
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(item_data)


def passenger_list(request):
    passengers = Passenger.objects.all()
    return render(request, "webapp/passenger_list.html", {"passengers": passengers})


def passenger_detail(request, id):
    passenger = get_object_or_404(Passenger, id=id)
    return render(request, "webapp/passenger_detail.html", {"passenger": passenger})


def passenger_add(request):
    if request.method == "POST":
        form = PassengerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("passenger_list")
    else:
        form = PassengerForm()

    return render(request, "webapp/passenger_form.html", {"form": form})


def passenger_edit(request, id):
    passenger = get_object_or_404(Passenger, id=id)

    if request.method == "POST":
        form = PassengerForm(request.POST, instance=passenger)
        if form.is_valid():
            form.save()
            return redirect("passenger_list")
    else:
        form = PassengerForm(instance=passenger)

    return render(request, "webapp/passenger_form.html", {"form": form})


def passenger_delete(request, id):
    passenger = get_object_or_404(Passenger, id=id)

    if request.method == "POST":
        passenger.delete()
        return redirect("passenger_list")

    return render(request, "webapp/passenger_delete.html", {"passenger": passenger})
