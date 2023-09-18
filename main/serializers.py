from rest_framework import serializers
from .models import Award, Chapter, MedicalMission

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = "__all__"

class MedicalMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalMission
        fields = "__all__"