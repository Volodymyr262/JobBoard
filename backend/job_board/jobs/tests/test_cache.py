import time
from unittest.mock import patch
from django.core.cache import cache
from hashlib import sha256
import pytest
from jobs.documents import JobDocument


@pytest.mark.django_db
def test_search_caches_results(client, job):
    from elasticsearch_dsl import Search

    # Index job into Elasticsearch
    JobDocument().update(job, refresh=True)

    query = "developer"
    page, page_size = 1, 10
    key = f"job-search:{sha256(f'{query}:{page}:{page_size}'.encode()).hexdigest()}"
    cache.clear()

    # First call - should query Elasticsearch
    with patch.object(Search, "execute", wraps=Search().execute) as mock_execute:
        response1 = client.get(f"/api/search/?q={query}&page={page}&page_size={page_size}")
        assert response1.status_code == 200
        assert cache.get(key) is not None
        assert mock_execute.call_count >= 1  # ✅ ES was queried

    # Second call - should return from cache
    with patch.object(Search, "execute", wraps=Search().execute) as mock_execute:
        response2 = client.get(f"/api/search/?q={query}&page={page}&page_size={page_size}")
        assert response2.status_code == 200
        assert response2.json() == response1.json()
        assert mock_execute.call_count == 0  # ✅ cache served
