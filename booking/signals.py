from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Payment

@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    if created or instance.status == 'confirmed':
        if instance.event:
            event = instance.event
            event.current_attendance = Booking.objects.filter(
                event=event,
                status='confirmed'
            ).count()
            event.save()
        if instance.business:
            business = instance.business
            business.total_bookings = Booking.objects.filter(
                business=business,
                status='confirmed'
            ).count()
            business.save()

@receiver(post_save, sender=Payment)
def update_booking_status(sender, instance, **kwargs):
    if instance.status == 'completed':
        instance.booking.status = 'confirmed'
        instance.booking.save()
    elif instance.status == 'failed':
        instance.booking.status = 'cancelled'
        instance.booking.save()
    elif instance.status == 'refunded':
        instance.booking.status = 'cancelled'
        instance.booking.save()