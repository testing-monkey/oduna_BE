from django.forms import Media
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from core.views import CoreGenericListView
from main.filters import AwardFilterBackend, MedicalMissionFilterBackend
from main.models import Award, MedicalMission
from main.serializers import AwardSerializer, MedicalMissionSerializer
from user.permissions import AdminPermission

# Create your views here.

class AwardListView(CoreGenericListView):
    """
    This API is used to Lists  Award.
    """

    schema_dict = {
        "summary": "Lists an new  Award",
    }
    permission_classes = []
    serializer_class = AwardSerializer
    filterset_class = AwardFilterBackend
    queryset = Award.objects.filter()


class AwardView(ListCreateAPIView, RetrieveUpdateAPIView):
    permission_classes = [AdminPermission]
    serializer_class = AwardSerializer
    filterset_class = AwardFilterBackend

class MedicalMissionListView(CoreGenericListView):
    """
    This API is used to Lists  MedicalMission.
    """

    schema_dict = {
        "summary": "Lists an new  MedicalMission",
    }
    permission_classes = []
    serializer_class = MedicalMissionSerializer
    filterset_class = MedicalMissionFilterBackend
    queryset = MedicalMission.objects.filter()


class MedicalMissionView(ListCreateAPIView, RetrieveUpdateAPIView):
    permission_classes = [AdminPermission]
    serializer_class = MedicalMissionSerializer
    filterset_class = MedicalMissionFilterBackend



   

