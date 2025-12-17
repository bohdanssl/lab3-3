from django import forms
from main.models import Passenger

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ["first_name", "last_name", "passport", "is_military", "is_student", "is_kid"]
