
from django.core.management.base import BaseCommand

from althingi.utils import update_issues


class Command(BaseCommand):

    help = 'Updates data'

    def handle(self, *args, **options):
        update_issues()
