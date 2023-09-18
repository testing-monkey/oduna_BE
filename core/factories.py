from datetime import datetime

import factory
import pytz
from factory import fuzzy


class CoreFactory(factory.django.DjangoModelFactory):
    created_at = fuzzy.FuzzyDateTime(datetime(2011, 8, 15, 8, 15, 12, 0, pytz.UTC))
    updated_at = fuzzy.FuzzyDateTime(datetime(2011, 8, 15, 8, 15, 12, 0, pytz.UTC))

    class Params:
        deleted = factory.Trait(
            active=False, is_deleted=True, deleted_at=datetime.now()
        )
