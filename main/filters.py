from .models import Award, MedicalMission
from core.filters import CoreFilterBackend


class AwardFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = Award
        exclude = ["is_deleted", "deleted_at", "non_member_recipient", "member_recipient"]

class MedicalMissionFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = MedicalMission
        exclude = ["is_deleted", "deleted_at", "participants"]