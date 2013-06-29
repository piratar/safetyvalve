from django.db import models
from django.contrib.auth.models import User

# Create your models here
class Petition(models.Model):
    name = models.CharField(max_length=500)
    resource = models.CharField(max_length=500)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class Signature(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    petition = models.ForeignKey(Petition, blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)