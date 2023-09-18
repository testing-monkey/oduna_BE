from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class UserType(TextChoices):
    MEMBER = "MEMBER", _("member")
    ADMIN = "ADMIN", _("admin")
    EXECUTIVE = "EXECUTIVE", _("executive")
    DEVELOPER = "DEVELOPER", _("developer")



class Gender(TextChoices):
    MALE = "MALE", _("male")
    FEMALE = "FEMALE", _("female")
    OTHER = "OTHER", _("other")
    PREFER_NOT_TO_SAY = "PREFER NOT TO SAY", _("preder not to say")



class PasswordChangeStatus(TextChoices):
    PENDING = "PENDING", _("PENDING")
    DONE = "DONE", _("DONE")
    CHANGE_PASSWORD = "CHANGE_PASSWORD", _("CHANGE_PASSWORD")
