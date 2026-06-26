from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Создаёт группу moderators, если её нет'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='moders')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "moders" создана'))
        else:
            self.stdout.write('Группа "moders" уже существует')