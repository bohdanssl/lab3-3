from .baserepo import BaseRepository
from .ticketrepo import TicketRepository
from main.models import Passenger, Train

class RepositoryManager:
    def __init__(self):
        self.passengers = BaseRepository(Passenger)
        self.trains = BaseRepository(Train)
        self.tickets = TicketRepository()
