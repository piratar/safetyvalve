
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from person.models import UserAuthentication

class Source(models.Model):
    name = models.CharField(max_length=50, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    # def __unicode__(self):
    #     return self.name

class PetitionManager(models.Manager):
    def search(self, search_string):
        results = Petition.objects.none()

        for word in search_string.split():
            result_part = Petition.objects.filter(Q(name__icontains=word) | Q(description__icontains=word) | Q(content__icontains=word))

            results = results | result_part

        # NOTE: One day ordering might be determined by relevance but for now it inherits the model's default ordering.
        return results

class Petition(models.Model):
    source = models.ForeignKey(Source)
    name = models.CharField(max_length=500)
    resource = models.CharField(max_length=500)

    # external_id is for external systems to identify their petitions. The format depends on those external systems.
    external_id = models.CharField(max_length=30)
    description = models.TextField()
    content = models.TextField()
    positive_notion = models.BooleanField(default=False)
    time_published = models.DateTimeField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    objects = PetitionManager()

    class Meta:
        ordering = ['-time_published', 'name']

    def __unicode__(self):
        return self.name

class Signature(models.Model):
    user = models.ForeignKey(User)
    petition = models.ForeignKey(Petition)
    authentication = models.ForeignKey(UserAuthentication)
    comment = models.CharField(max_length=500)
    stance = models.CharField(max_length=50)
    show_public = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    mail_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s signed "%s"' % (self.user, self.petition)
