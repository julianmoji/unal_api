import graphene
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required

from core.grade_scoring.input import StudentInput, SubjectStudentInput, UpdateSubjectStudentInput
from core.grade_scoring.models import Student, SubjectStudent
from core.grade_scoring.types import SubjectStudentType
from core.mixins import MutationMixinErrors
from core.utils import clean_global_ids


class CreateSubjectStudentList(graphene.Mutation, MutationMixinErrors):
    class Arguments:
        student_data = StudentInput(required=True)
        subject_student_data = graphene.List(of_type=SubjectStudentInput, required=True)

    subject_student_list = graphene.List(of_type=SubjectStudentType, required=True)

    @login_required
    def mutate(self, info, **kwargs):
        errors = []
        try:
            data = clean_global_ids(kwargs)
        except ValueError as e:
            return CreateSubjectStudentList(error=True, errors=e.args[0], subject_student_list=[])

        subject_student_list = []
        student, _ = Student.objects.get_or_create(**data.pop("student_data"))
        subject_student_data = data.get("subject_student_data", [])
        for item in subject_student_data:
            item["student_id"] = student.id
            try:
                instance, created = SubjectStudent.objects.get_or_create(**item)
                subject_student_list.append(instance)
            except ValidationError as e:
                errors.append(e.args[0])

        return CreateSubjectStudentList(subject_student_list=subject_student_list, errors="\n".join(errors))


class UpdateSubjectStudent(graphene.Mutation, MutationMixinErrors):
    class Arguments:
        data = UpdateSubjectStudentInput(required=True)

    subject_student = graphene.Field(SubjectStudentType)

    @login_required
    def mutate(self, info, data=None):
        try:
            data = clean_global_ids(data)
        except ValueError as e:
            return UpdateSubjectStudent(error=True, errors=e.args[0], subject_student_list=[])

        pk = data.pop("id")
        subject_student = SubjectStudent.objects.get(pk=pk)
        for key, value in data.items():
            setattr(subject_student, key, value)
        subject_student.save(update_fields=data.keys())
        subject_student.refresh_from_db()
        return UpdateSubjectStudent(subject_student=subject_student)
