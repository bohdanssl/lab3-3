from django.contrib import admin
from .models import Passenger, Train, Ticket

# Register your models here.
admin.site.register(Passenger)
admin.site.register(Train)
admin.site.register(Ticket)