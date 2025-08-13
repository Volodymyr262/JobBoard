import time
from unittest.mock import patch
from django.core.cache import cache
from hashlib import sha256
import pytest


@pytest.mark.django_db
def test_search_caches_results(client, job):
    from elasticsearch_dsl import Search

    query = "developer"
    key = f"job-search:{sha256(query.encode()).hexdigest()}"
    cache.clear()

    # First call - should query Elasticsearch
    with patch.object(Search, "execute", wraps=Search().execute) as mock_execute:
        response1 = client.get(f"/api/search/?q={query}")
        assert response1.status_code == 200
        assert cache.get(key) is not None
        assert mock_execute.call_count >= 1  # ES was queried

    # Second call - should return from cache
    with patch.object(Search, "execute", wraps=Search().execute) as mock_execute:
        response2 = client.get(f"/api/search/?q={query}")
        assert response2.status_code == 200
        assert response2.json() == response1.json()
        assert mock_execute.call_count == 0
