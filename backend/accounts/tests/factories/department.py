import factory
from factory.django import DjangoModelFactory

from accounts.models.department import Department


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"department{n}")
    description = factory.Faker("sentence", nb_words=5)
