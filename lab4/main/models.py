from django.db import models

class Passenger(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    passport = models.CharField(max_length=30, unique=True)
    is_military = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_kid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]


class Train(models.Model):
    train_number = models.CharField(max_length=30, unique=True)
    begin_point = models.CharField(max_length=50)
    end_point = models.CharField(max_length=50)

    def __str__(self):
        return f"Train {self.train_number}: {self.begin_point} → {self.end_point}"

    class Meta:
        ordering = ["train_number"]


class Ticket(models.Model):
    class TicketType(models.TextChoices):
        PLAZKART = 'PL', 'Plazkart'
        KUPE = 'KP', 'Kupe'
        LUX = 'LX', 'Lux'

    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="tickets")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.CharField(
        max_length=2,
        choices=TicketType.choices,
        default=TicketType.PLAZKART,
    )

    price = models.DecimalField(max_digits=8, decimal_places=2)
    date_purchased = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket ({self.ticket_type}) - {self.passenger}"

    class Meta:
        ordering = ["-date_purchased"]
