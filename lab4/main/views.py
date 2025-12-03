from django.shortcuts import render
from rest_framework import viewsets, status
from .serializers import *
from main.repositories.repomanager import RepositoryManager
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

repo = RepositoryManager()

class TrainViewSet(viewsets.ModelViewSet):
	queryset = repo.trains.get_all()
	serializer_class = TrainSerializer

class PassengerViewSet(viewsets.ModelViewSet):
	queryset = repo.passengers.get_all()
	serializer_class = PassengerSerializer

class TicketViewSet(viewsets.ModelViewSet):
	queryset = repo.tickets.get_all()
	serializer_class = TicketSerializer
	

class TicketReport(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tickets = repo.tickets.get_all()
        total_tickets = tickets.count()  # якщо tickets - QuerySet
        total_money = sum(ticket.price for ticket in tickets)

        report = {
            "total_tickets": total_tickets,
            "total_income": total_money,
            "average_price": total_money / total_tickets if total_tickets else 0
        }

        return Response(report, status=status.HTTP_200_OK)
    
