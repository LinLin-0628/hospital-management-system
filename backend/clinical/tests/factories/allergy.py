import factory
from factory.django import DjangoModelFactory

from clinical.models.allergy import Allergy


class AllergyFactory(DjangoModelFactory):
    class Meta:
        model = Allergy

    # Unique, lowercase-safe name
    name = factory.Sequence(lambda n: f"allergy{n}")

    # Short valid description (model will strip it)
    description = factory.Faker("sentence", nb_words=5)
