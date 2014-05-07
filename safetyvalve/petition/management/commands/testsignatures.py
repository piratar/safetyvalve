from random import randrange
from sys import stdout

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from petition.models import Petition, Signature
from person.models import UserAuthentication

class Command(BaseCommand):

    help = 'Generates test signatures for all found issues'

    def handle(self, *args, **options):

        petition_count = 100
        signatures_min = 20
        signatures_max = 30

        user, newly_created = User.objects.get_or_create(username='1234567891', first_name='Test User')

        petitions = Petition.objects.all().order_by('?')[:petition_count]
        for petition in petitions:

            signatures_count = randrange(signatures_min, signatures_max + 1)

            stdout.write("Generating %d signatures for petition '%s'" % (signatures_count, petition.name))
            stdout.flush()

            for i in range(0, signatures_count):
                random_number = 0 # Just for formality's sake, really.
                user = None
                while user is None:
                    random_number = randrange(100000, 999999)
                    random_username = 'test_user_%d' % random_number
                    random_name = 'Tester nr. %d' % random_number
                    if User.objects.filter(username=random_username).count() == 0:
                        user = User.objects.create(username=random_username)
                        user.first_name = random_name
                        user.save()

                # Generate a test authentication
                auth = UserAuthentication()
                auth.user = user
                auth.method = 'test'
                auth.token = 'test_%d' % random_number
                auth.save()

                # Generate a test signature
                sig = Signature()
                sig.user = user
                sig.petition = petition
                sig.authentication = auth
                sig.show_public = True
                sig.save()

                stdout.write(".")
                stdout.flush()

            stdout.write(" done\n")
            stdout.flush()


