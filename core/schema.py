from django.conf import settings
from drf_spectacular.openapi import AutoSchema as SpecAutoSchema
from drf_spectacular.utils import OpenApiParameter


class AutoSchema(SpecAutoSchema):
    def __init__(self):
        super().__init__()
        self.summary = ""
        self.tags = []

    global_params = [
        OpenApiParameter(
            name="x-api-key",
            type=str,
            default=settings.PLATFORM_KEY,
            location=OpenApiParameter.HEADER,
            description="`This is the api-key associated with the environment",
        )
    ]

    def get_override_parameters(self):
        params = super().get_override_parameters()
        return params + self.global_params

    def get_summary(self):
        return self.summary

    def get_tags(self):
        return super().get_tags() + self.tags

    def get_operation(self, path, path_regex, path_prefix, method, registry):
        schema_dict = getattr(self.view, "schema_dict", {})
        self.summary = schema_dict.get("summary", "")
        if not self.summary:
            self.summary = schema_dict.get("summary__" + method.lower(), "")
        self.tags = schema_dict.get("tags", [])
        return super().get_operation(path, path_regex, path_prefix, method, registry)
