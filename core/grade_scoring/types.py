import graphene
from graphene_django.types import DjangoObjectType

from core.grade_scoring.models import Subject, Student, SubjectStudent
from core.utils import AggregateConnection


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        filter_fields = {"name": ["exact"]}
        interfaces = (graphene.relay.Node,)


class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        interfaces = (graphene.relay.Node,)
        filter_fields = {"document_number", "document_type"}


class SubjectStudentType(DjangoObjectType):
    average = graphene.Decimal(description="overall average")

    class Meta:
        model = SubjectStudent
        interfaces = (graphene.relay.Node,)
        connection_class = AggregateConnection
        filter_fields = {
            "student__document_type": ["exact"],
            "student__document_number": ["exact"],
            "passed": ["exact"],
        }
