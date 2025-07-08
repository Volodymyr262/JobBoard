from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry
from .models import Job

@receiver(post_save, sender=Job)
def update_job_document(sender, instance, **kwargs):
    registry.update(instance)

@receiver(post_delete, sender=Job)
def delete_job_document(sender, instance, **kwargs):
    registry.delete(instance)