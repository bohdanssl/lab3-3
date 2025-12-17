from django.db.models import Count, Sum, Avg, F, Q, Max, Min
from main.models import Train, Passenger, Ticket
from .baserepo import BaseRepository 

class StatsRepository:


    # Потяги за прибутковістю 
    @staticmethod
    def get_trains_by_revenue():
        return Train.objects.annotate(
            total_revenue=Sum('tickets__price'),
            tickets_sold=Count('tickets')
        ).order_by('-total_revenue')

    # Пасажири, які витратили більше певної суми 
    @staticmethod
    def get_top_spending_passengers(min_spent=1000):
        return Passenger.objects.annotate(
            total_spent=Sum('tickets__price'),
            trips_count=Count('tickets')
        ).filter(total_spent__gt=min_spent).order_by('-total_spent')

    # Статистика по типах квитків для кожного потяга 
    @staticmethod
    def get_ticket_types_per_train():
        return Train.objects.annotate(
            plazkart_count=Count('tickets', filter=Q(tickets__ticket_type=Ticket.TicketType.PLAZKART)),
            kupe_count=Count('tickets', filter=Q(tickets__ticket_type=Ticket.TicketType.KUPE)),
            lux_count=Count('tickets', filter=Q(tickets__ticket_type=Ticket.TicketType.LUX)),
        ).filter(tickets__isnull=False).distinct()

    # Середня вартість квитка по маршрутах 
    
    @staticmethod
    def get_avg_price_per_route():
        return Ticket.objects.values(
            'train__begin_point', 'train__end_point'
        ).annotate(
            avg_price=Avg('price'),
            max_price=Max('price'),
            trips=Count('id')
        ).order_by('-avg_price')

    # Аналіз пільг
    @staticmethod
    def get_social_stats_by_train():
        return Train.objects.annotate(
            military_count=Count('tickets', filter=Q(tickets__passenger__is_military=True)),
            student_count=Count('tickets', filter=Q(tickets__passenger__is_student=True)),
            total_passengers=Count('tickets')
        ).filter(total_passengers__gt=0).order_by('-student_count')

    # Пасажири які тільки в люксі
    @staticmethod
    def get_luxury_only_passengers():
        return Passenger.objects.annotate(
            lux_tickets=Count('tickets', filter=Q(tickets__ticket_type=Ticket.TicketType.LUX)),
            total_tickets=Count('tickets')
        ).filter(
            total_tickets__gt=0,
            lux_tickets=F('total_tickets') 
        )
    
    #для plotly
    @staticmethod
    def get_all_departure_cities():
        return Train.objects.values_list('begin_point', flat=True)\
                            .exclude(begin_point__isnull=True)\
                            .distinct()\
                            .order_by('begin_point')