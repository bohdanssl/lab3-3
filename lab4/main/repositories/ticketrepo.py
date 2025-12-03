from .baserepo import BaseRepository
from main.models import Ticket

class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    def calculate_discount(self, ticket: Ticket):
        price = ticket.price
        if ticket.passenger.is_student:
            price *= 0.8  
        if ticket.passenger.is_military:
            price *= 0.5  
        if ticket.passenger.is_kid:
            price *= 0.7  
        return round(price, 2)

    def create(self, **kwargs):
        ticket = super().create(**kwargs)
        discounted_price = self.calculate_discount(ticket)
        ticket.price = discounted_price
        ticket.save()
        return ticket

    def update(self, obj_id, **kwargs):
        ticket = super().update(obj_id, **kwargs)
        if ticket:
            ticket.price = self.calculate_discount(ticket)
            ticket.save()
        return ticket
