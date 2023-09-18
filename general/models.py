from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import CoreModel, DeleteModelMixin
from general.choices import ActionStatus, MediaType


class Category(DeleteModelMixin, CoreModel):
    name = models.CharField(_("Name"), max_length=100)

class Media(DeleteModelMixin,CoreModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='files') 
    type = models.CharField(
        _("media type"),
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    visible = models.BooleanField(_("visible"), default=True)
    tags = models.ManyToManyField(Category)

class NewsletterSubscriber(DeleteModelMixin, CoreModel):
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return f"{self.email}"
    
class ContactUs(DeleteModelMixin, CoreModel):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    status = models.CharField(default=ActionStatus.PENDING, max_length=15)

