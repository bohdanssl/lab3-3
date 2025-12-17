from django.db.models import Sum, Count
from .baserepo import BaseRepository
from main.models import Passenger

class PassengerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Passenger)

    