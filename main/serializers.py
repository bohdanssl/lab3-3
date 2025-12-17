from rest_framework import serializers
from .models import Passenger, Train, Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
    
class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'