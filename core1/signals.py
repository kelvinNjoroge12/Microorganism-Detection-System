import django.db.models.signals
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(django.db.models.signals.post_migrate)
def setup_groups(sender, **kwargs):
    """Create default groups after migrations"""
    Group.objects.get_or_create(name='Admins')
    Group.objects.get_or_create(name='Researchers')
    Group.objects.get_or_create(name='Regular Users')