from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from core.grade_scoring.models import Subject, Student, SubjectStudent
from core.grade_scoring.mutations import CreateSubjectStudentList, UpdateSubjectStudent
from core.grade_scoring.types import SubjectType, StudentType, SubjectStudentType


class Query(object):
    subjects = DjangoFilterConnectionField(SubjectType)

    @login_required
    def resolve_subjects(self, info, **kwargs):
        return Subject.objects.all()

    student = DjangoFilterConnectionField(StudentType)

    @login_required
    def resolve_student(self, info, **kwargs):
        return Student.objects.all()

    subject_student = DjangoFilterConnectionField(SubjectStudentType)

    @login_required
    def resolve_subject_student(self, info, **kwargs):
        return SubjectStudent.objects.all()


class Mutation(object):
    create_subject_student_list = CreateSubjectStudentList.Field()
    update_subject_student = UpdateSubjectStudent.Field()
