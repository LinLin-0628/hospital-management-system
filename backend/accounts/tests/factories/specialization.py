import factory
from factory.django import DjangoModelFactory

from accounts.models.specialization import Specialization
from accounts.tests.factories.department import DepartmentFactory


class SpecializationFactory(DjangoModelFactory):
    class Meta:
        model = Specialization
        django_get_or_create = ("name",)

    # Unique, lowercase, valid name
    name = factory.Sequence(lambda n: f"specialization{n}")

    # FK dependency
    department = factory.SubFactory(DepartmentFactory)
