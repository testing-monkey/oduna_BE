import csv
import logging

from django.core.cache import cache
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from core.serializers import FileUploadSerializer
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from user.permissions import AdminPermission
from rest_framework import status

# logger = logging.get# logger("main")


# Create your views here.
class CoreGenericListView(ListAPIView):
    pass






class LoggingTest(GenericAPIView):
    """
    This API is for Testing Logging
    """

    schema_dict = {
        "summary": "Test Logging (Note: For Debug Only) ",
    }
    permission_classes = [AdminPermission]

    @extend_schema(
        parameters=[
            OpenApiParameter("message", str, required=True),
        ],
        responses={
            200: OpenApiResponse(
                description="Success.",
                examples=[OpenApiExample(name="example 1", value=["string"])],
                response=[OpenApiTypes.STR],
            )
        },
    )
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query_params = self.request.query_params
            message = query_params.get("message")
            # logger.info("message: %s", message)
            logging.info("message2: %s", message)
            return HttpResponse("Log message Saved On server")
        return HttpResponse("Not Permitted")



