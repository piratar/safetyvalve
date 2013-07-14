
from django.db import models
from django.contrib.auth.models import User

from person.models import UserAuthentication


class Petition(models.Model):
    name = models.CharField(max_length=500)
    resource = models.CharField(max_length=500)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Signature(models.Model):
    user = models.ForeignKey(User)
    petition = models.ForeignKey(Petition)
    authentication = models.ForeignKey(UserAuthentication)
    comment = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
