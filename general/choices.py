from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ActionStatus(TextChoices):
    PENDING = "PENDING", _("PENDING")
    ACCEPTED = "ACCEPTED", _("ACCEPTED")
    IN_PROGRESS = "IN_PROGRESS", _("IN_PROGRESS")
    COMPLETED = "COMPLETED", _("COMPLETED")
    DECLINED = "DECLINED", _("DECLINED")



class MediaType(TextChoices):
    VIDEO = "VIDEO", _("video")
    IMAGE = "IMAGE", _("image")
    OTHERS = "OTHERS", _("others")
    FILE = "FILE", _("file")