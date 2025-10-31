# Generated migration to update existing StudentAnswer records with current timestamp

from django.db import migrations
from django.utils import timezone


def update_timestamps(apps, schema_editor):
    StudentAnswer = apps.get_model('maths', 'StudentAnswer')
    # Update all records to have current timestamp if they somehow don't have one
    # Since answered_at has auto_now_add=True, all records should have timestamps
    # This is a safety measure to ensure all records are updated
    now = timezone.now()
    StudentAnswer.objects.filter(answered_at__isnull=True).update(answered_at=now)
    # Also update records grouped by session_id to have the same timestamp for the first answer
    # This ensures all answers in a session have consistent timestamps
    from django.db.models import Min
    for session_id in StudentAnswer.objects.exclude(session_id='').values_list('session_id', flat=True).distinct():
        first_answer = StudentAnswer.objects.filter(session_id=session_id).order_by('id').first()
        if first_answer:
            StudentAnswer.objects.filter(session_id=session_id).update(answered_at=first_answer.answered_at)


def reverse_update(apps, schema_editor):
    # No reverse operation needed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0004_alter_studentanswer_session_id'),
    ]

    operations = [
        migrations.RunPython(update_timestamps, reverse_update),
    ]

