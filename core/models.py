import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.managers import CustomManager

# Create your models here.


class CoreModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return self.__str__()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    @classmethod
    def from_validated_data(cls, validated_data: dict, *args, **kwargs):
        fields = [field.name for field in cls._meta.fields]

        constructor_kwargs = {
            field: validated_data.pop(field)
            for field in fields
            if field in validated_data
        }
        return cls(**constructor_kwargs)

    def update_from_validated_data(self, validated_data: dict, *args, **kwargs):
        fields = [field.name for field in self._meta.fields]

        for field in fields:
            if field in validated_data:
                setattr(self, field, validated_data.pop(field))

        self.save()

    @classmethod
    def read_only_fields(cls):
        return [
            "created_at",
            "id",
        ]

    @classmethod
    def get_hidden_fields(cls, extra_fields=()):
        return ["updated_at", "is_deleted", "deleted_at"] + list(extra_fields)

    class Meta:
        abstract = True


class DeleteModelMixin(models.Model):
    all_objects = models.Manager()
    objects = CustomManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()





class GeographicInfoModel(models.Model):
    class UserRegion(models.TextChoices):
        AFRICA = "AF", _("Africa")
        ASIA = "AS", _("Asia")
        EUROPE = "EU", _("Europe")
        MIDDLE_EAST = "ME", _("Middle East")
        NORTH_AMERICA = (
            "NA",
            _("North America"),
        )
        SOUTH_AMERICA = "SA", _("South America")

    street = models.CharField(_("street"), max_length=100)
    zipcode = models.CharField(_("street"), max_length=100)
    district = models.CharField(_("street"), max_length=100, null=True, blank=True)
    city = models.CharField(_("city"), max_length=50)
    state = models.CharField(_("state"), max_length=50)
    country = models.CharField(_("country"), max_length=50, default="NG")
    region = models.CharField(
        _("region"),
        max_length=50,
        choices=UserRegion.choices,
        default=UserRegion.AFRICA,
    )


    class Meta:
        abstract = True
