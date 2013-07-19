
from django.db import models
from django.contrib.auth.models import User

from person.models import UserAuthentication


class Petition(models.Model):
    name = models.CharField(max_length=500)
    resource = models.CharField(max_length=500)
    # external_id is for external systems to identify their petitions. The format depends on those external systems.
    external_id = models.CharField(max_length=30)
    description = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Signature(models.Model):
    user = models.ForeignKey(User)
    petition = models.ForeignKey(Petition)
    authentication = models.ForeignKey(UserAuthentication)
    comment = models.CharField(max_length=500)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s signed "%s"' % (self.user, self.petition)

