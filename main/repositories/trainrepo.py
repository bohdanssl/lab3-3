from django.db.models import Sum, Count, Avg, Q, F, Max
from .baserepo import BaseRepository
from main.models import Train

class TrainRepository(BaseRepository):
    def __init__(self):
        super().__init__(Train)

    