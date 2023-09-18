from django.db import models
from django.contrib.postgres.fields import ArrayField
from general.models import Media
from core.models import CoreModel, DeleteModelMixin
from user.models import User

# Create your models here.

class Chapter(DeleteModelMixin, CoreModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    members = models.ManyToManyField(User)

class Award(DeleteModelMixin, CoreModel):
    name = models.CharField(max_length=100)
    non_member_recipient =  ArrayField(models.CharField(max_length=200), blank=True, null=True)
    member_recipient =  models.ManyToManyField(User)

class MedicalMission(DeleteModelMixin, CoreModel):
    name = models.CharField(max_length=100)
    participants = models.ManyToManyField(User)
    media = models.ManyToManyField(Media)