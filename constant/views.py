import json

from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class Country(APIView):
    """
    This API is to get all countries
    """

    schema_dict = {
        "summary__get": "Get All countries",
    }
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Success.",
                examples=[
                    OpenApiExample(
                        name="example 1",
                        value=[{"name": "string", "country_code": "string"}],
                    )
                ],
                response=[OpenApiTypes.STR],
            )
        },
    )
    def get(self, *args, **kwargs):
        data = json.load(open(settings.BASE_DIR / "json" / "country.json"))
        return Response({"status_code": 200, "message": "Success.", "result": data})


class State(APIView):
    """
    This API is to get all state by countries
    """

    schema_dict = {
        "summary__get": "Get All state by countries",
    }
    permission_classes = (AllowAny,)

    @extend_schema(
        parameters=[
            OpenApiParameter("country_code", str, required=True),
        ],
        responses={
            200: OpenApiResponse(
                description="Success.",
                examples=[
                    OpenApiExample(
                        name="example 1",
                        value=[{"name": "string", "state_code": "string"}],
                    )
                ],
                response=[OpenApiTypes.STR],
            )
        },
    )
    def get(self, *args, **kwargs):
        data = json.load(open(settings.BASE_DIR / "json" / "state.json"))
        query_params = self.request.query_params
        if "country_code" not in query_params:
            raise ValidationError("country_code is required.")
        try:
            return Response(
                {
                    "status_code": 200,
                    "message": "Success.",
                    "result": data[query_params["country_code"]],
                }
            )
        except KeyError:
            return Response(
                {"status_code": 404, "message": "Not found.", "result": []}, status=404
            )


class City(APIView):
    """
    This API is to get all cities by countries and state
    """

    schema_dict = {
        "summary__get": "Get All cities by countries and state",
    }
    permission_classes = (AllowAny,)

    @extend_schema(
        parameters=[
            OpenApiParameter("country_code", str, required=True),
            OpenApiParameter("state_code", str, required=True),
        ],
        responses={
            200: OpenApiResponse(
                description="Success.",
                examples=[OpenApiExample(name="example 1", value=["string"])],
                response=[OpenApiTypes.STR],
            )
        },
    )
    def get(self, *args, **kwargs):
        data = json.load(open(settings.BASE_DIR / "json" / "city.json"))
        query_params = self.request.query_params
        if "country_code" not in query_params and "state_code" not in query_params:
            raise ValidationError("country_code and status_code are required.")
        try:
            return Response(
                {
                    "status_code": 200,
                    "message": "Success.",
                    "result": data[query_params["country_code"]][
                        query_params["state_code"]
                    ],
                }
            )
        except KeyError:
            return Response(
                {"status_code": 404, "message": "Not found.", "result": []}, status=404
            )
