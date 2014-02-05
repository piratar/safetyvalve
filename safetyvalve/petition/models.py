
from django.db import models
from django.contrib.auth.models import User

from person.models import UserAuthentication

class Source(models.Model):
    name = models.CharField(max_length=50, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    # def __unicode__(self):
    #     return self.name

class Petition(models.Model):
    source = models.ForeignKey(Source)
    name = models.CharField(max_length=500)
    resource = models.CharField(max_length=500)

    # external_id is for external systems to identify their petitions. The format depends on those external systems.
    external_id = models.CharField(max_length=30)
    description = models.TextField()
    content = models.TextField()
    positive_notion = models.BooleanField(default=False)
    timing_published = models.DateTimeField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timing_published', 'name']

    def __unicode__(self):
        return self.name

class Signature(models.Model):
    user = models.ForeignKey(User)
    petition = models.ForeignKey(Petition)
    authentication = models.ForeignKey(UserAuthentication)
    comment = models.CharField(max_length=500)
    show_public = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    mail_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s signed "%s"' % (self.user, self.petition)
