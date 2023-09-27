from django.db import models
from graphql_relay import to_global_id
from model_utils.models import TimeStampedModel


class Subject(models.Model):
    name = models.CharField(max_length=400, unique=True, blank=False)
    required_subjects = models.ManyToManyField(
        "Subject",
        help_text="Save the subjects that must be approved by the student in order to enroll in this subject",
    )

    @property
    def uuid(self):
        return to_global_id("SubjectType", self.id)

    class Meta:
        db_table = "unal_subject"

    def __str__(self):
        return self.name


class Student(TimeStampedModel):
    CC = "cc"
    TI = "ti"
    CE = "ce"
    DOCUMENT_TYPE = (
        (CC, "Citizenship card"),
        (TI, " Identity card"),
        (CE, "Foreigner identification card"),
    )
    document_type = models.CharField(choices=DOCUMENT_TYPE, max_length=4)
    document_number = models.TextField(default="")

    def valid_to_enroll_subject(self, subject: Subject) -> bool:
        """
        This function checks if the student has passed the required_subjects of subject in order to enroll it
        """
        if required_subjects_pks := subject.required_subjects.values_list("pk", flat=True):
            return (
                self.subjectstudent_set.filter(subject__pk__in=required_subjects_pks, passed=True).count()
                == required_subjects_pks.count()
            )
        return True

    class Meta:
        db_table = "unal_student"
        unique_together = (("document_type", "document_number"),)

    def __str__(self):
        return str(self.pk)


class SubjectStudent(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    passed = models.BooleanField(default=False, help_text="Indicates whether the student passed the subject")
    score = models.FloatField(blank=True, null=True, default=None, help_text="Indicates the current score")
    unique_together = ("subject", "student")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "subject"], name="student_and_subject_unique_together")
        ]

    def pass_the_subject(self, commit=True) -> bool:
        if self.score:
            self.passed = self.score >= 3.0
        if commit:
            self.save(update_fields=["passed"])
        return self.passed
