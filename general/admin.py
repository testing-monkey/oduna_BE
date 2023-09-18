from django.contrib import admin

from .models import ContactUs

# Register your models here.


models = [

    {"model": ContactUs, "resource": []},
]
for model in models:
    admin.site.register(model["model"], *model["resource"])
