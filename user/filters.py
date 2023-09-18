from core.filters import CoreFilterBackend

from django.contrib.auth.models import Permission, Group

from user.models import User





class UserFilterBackend(CoreFilterBackend):
    class Meta:
        model = User
        exclude = ["image"]
