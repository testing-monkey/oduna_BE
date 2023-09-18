from django.urls import path

from .views import AwardListView, AwardView, MedicalMissionListView, MedicalMissionView


urlpatterns = [
    path("awards/", AwardView.as_view(), name="award_list_create"),
    path("awards/list", AwardListView.as_view(), name="award_list"),
    path("medical-missions/", MedicalMissionView.as_view(), name="medical_mission_list_create"),
    path("medical-missions/list", MedicalMissionListView.as_view(), name="medical_mission_list"),
]
