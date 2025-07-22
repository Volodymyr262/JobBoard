from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Job

job_index = Index("jobs")
job_index.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        "analyzer": {
            "autocomplete_analyzer": {
                "type": "custom",
                "tokenizer": "autocomplete_tokenizer",
                "filter": ["lowercase"]
            },
            "autocomplete_search": {
                "type": "custom",
                "tokenizer": "lowercase"
            }
        },
        "tokenizer": {
            "autocomplete_tokenizer": {
                "type": "edge_ngram",
                "min_gram": 2,
                "max_gram": 20,
                "token_chars": ["letter", "digit"]
            }
        }
    }
)


@registry.register_document
class JobDocument(Document):
    company = fields.ObjectField(properties={"name": fields.TextField()})
    location = fields.ObjectField(properties={"city": fields.TextField(), "country": fields.TextField()})

    title = fields.TextField(analyzer="autocomplete_analyzer", search_analyzer="autocomplete_search")
    description = fields.TextField(analyzer="autocomplete_analyzer", search_analyzer="autocomplete_search")

    # 🔥 Add this line:
    suggest = fields.CompletionField()

    class Index:
        name = "jobs"
        settings = job_index._settings

    class Django:
        model = Job
        fields = ['job_type', 'experience_level', 'created_at']

    def prepare_suggest(self, instance):
        return {
            "input": [instance.title],  # Suggestions from job title
            "weight": 10
        }
