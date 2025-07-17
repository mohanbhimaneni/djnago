from django.db import models
from django.contrib.auth.models import User 
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Movie(models.Model):
    name= models.CharField(max_length=255)
    image= models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3,decimal_places=1)
    cast= models.TextField()
    description= models.TextField(blank=True,null=True) # optional

    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='theaters')
    time= models.DateTimeField()

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE,related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked=models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'

class Booking(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    seat=models.OneToOneField(Seat,on_delete=models.CASCADE)
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    theater=models.ForeignKey(Theater,on_delete=models.CASCADE)
    booked_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Booking by{self.user.username} for {self.seat.seat_number} at {self.theater.name}'

@receiver(post_save, sender=Booking)
def mark_seat_booked(sender, instance, created, **kwargs):
    # Mark seat as booked when a booking is created
    if created:
        seat = instance.seat
        if not seat.is_booked:
            seat.is_booked = True
            seat.save(update_fields=['is_booked'])

@receiver(post_delete, sender=Booking)
def mark_seat_unbooked(sender, instance, **kwargs):
    # Mark seat as unbooked when a booking is deleted
    seat = instance.seat
    if seat.is_booked:
        seat.is_booked = False
        seat.save(update_fields=['is_booked'])