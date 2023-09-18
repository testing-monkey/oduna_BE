from rest_framework import serializers
from core.serializers import Base64ImageField
from general.literals import MAXIMUM_NEWSLETTER_FILE_SIZE
from .models import Media
from general.models import NewsletterSubscriber
from rest_framework.exceptions import ValidationError
class ContactUsSerializer(serializers.Serializer):
    subject = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField()
    message = serializers.CharField()

class NewsletterSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(), required=True)
    subject = serializers.CharField(required=True, max_length=100)
    file = Base64ImageField(max_length=None, use_url=True, required=False)
    message = serializers.CharField(max_length=10_000)

    def validate_file(self, attrs):
        if attrs:
            if attrs.size < (2 * pow(2, 10)):
                raise ValidationError(MAXIMUM_NEWSLETTER_FILE_SIZE)
        return super().validate(attrs)
    
class NewsletterSubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = "__all__"

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"

