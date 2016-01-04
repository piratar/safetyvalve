
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from althingi.althingi_settings import CURRENT_SESSION_NUM

from person.models import UserAuthentication

class Source(models.Model):
    name = models.CharField(max_length=50, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    # def __unicode__(self):
    #     return self.name

class PetitionManager(models.Manager):
    # Example usage: Petition.objects.search('searchstring', 'name,description')
    def search(self, search_string, search_fields=['name', 'description', 'content']):
        results = Petition.objects.none()

        # Must look somewhere.
        if len(search_fields) == 0:
            return results

        for word in search_string.split():
            q = Q()

            if 'name' in search_fields:
                kwargs = {'name__icontains': word}
                q = q | Q(**kwargs)
            if 'description' in search_fields:
                kwargs = {'description__icontains': word}
                q = q | Q(**kwargs)
            if 'content' in search_fields:
                kwargs = {'content__icontains': word}
                q = q | Q(**kwargs)

            result_part = Petition.objects.filter(q, external_id__startswith=CURRENT_SESSION_NUM)

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

    def __str__(self):
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

    def __str__(self):
        return u'%s signed "%s"' % (self.user, self.petition)
