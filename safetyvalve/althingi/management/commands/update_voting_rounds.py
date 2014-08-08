from django.core.management.base import BaseCommand

from althingi.utils import update_voting_rounds


class Command(BaseCommand):

    help = 'Updates data'

    def handle(self, *args, **options):
        update_voting_rounds(*args)
