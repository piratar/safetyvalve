from django.db import models
from django.contrib.auth.models import User

from person.auth import AUTHENTICATION_NAME_MAX_LENGTH


class UserAuthentication(models.Model):
    user = models.ForeignKey(User)
    method = models.CharField(max_length=AUTHENTICATION_NAME_MAX_LENGTH)
    token = models.TextField()
    generated = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.token, self.generated)


'''

1. New user enters system. Sees petition. Starts to sign. Obtains IceKey. Signes.

'''
