from core.grade_scoring.models import Student, Subject, SubjectStudent
from core.inputs import Input


class StudentInput(Input):
    class Meta:
        model = Student
        only_fields = [field.name for field in model._meta._get_fields(reverse=False, include_parents=False)]
        exclude_fields = ("id", "created", "modified")


class SubjectInput(Input):
    class Meta:
        model = Subject
        only_fields = ["id"]


class SubjectStudentInput(Input):
    class Meta:
        model = SubjectStudent
        only_fields = ["subject"]
        exclude_fields = ("student", "passed", "score")


class UpdateSubjectStudentInput(Input):
    class Meta:
        model = SubjectStudent
        only_fields = ["id", "score"]
        optional_fields = [
            field.name for field in model._meta._get_fields(reverse=False, include_parents=False) if field.name != "id"
        ]
