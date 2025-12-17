from .baserepo import BaseRepository
from .ticketrepo import TicketRepository
from .trainrepo import TrainRepository
from .passengerrepo import PassengerRepository
from main.models import Passenger, Train

class RepositoryManager:
    def __init__(self):
        self.passengers = PassengerRepository()
        self.trains = TrainRepository()
        self.tickets = TicketRepository()
