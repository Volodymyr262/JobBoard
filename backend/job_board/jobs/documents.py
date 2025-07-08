from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Job

# Define the Elasticsearch index
job_index = Index("jobs")
job_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)

@registry.register_document
class JobDocument(Document):
    company = fields.ObjectField(properties={
        "name": fields.TextField(),
    })

    location = fields.ObjectField(properties={
        "city": fields.TextField(),
        "country": fields.TextField(),
    })

    class Index:
        name = 'jobs'

    class Django:
        model = Job
        fields = [
            'title',
            'description',
            'job_type',
            'experience_level',
            'created_at',
        ]
