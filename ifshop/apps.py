from django.apps import AppConfig


class IfshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ifshop'

def ready(self):
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name='Vendedor')