from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import (
    SubjectStudent,
)


@receiver(pre_save, sender=SubjectStudent)
def pre_save_subject_student(sender, instance, **kwargs):
    subject = instance.subject
    if not instance.pk:
        if not instance.student.valid_to_enroll_subject(subject=subject):
            raise ValidationError(
                f"The student has not passed the required subjects to enroll the subject {subject.name}"
            )


@receiver(post_save, sender=SubjectStudent)
def post_save_subject_student(sender, instance, created, **kwargs):
    post_save.disconnect(post_save_subject_student, sender=sender)
    instance.pass_the_subject(commit=True)
    post_save.connect(post_save_subject_student, sender=sender)
