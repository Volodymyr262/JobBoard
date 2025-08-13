from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from jobs.documents import JobDocument
from .models import Job, Location, CompanyProfile, SavedJob
from .serializers import JobSerializer, CompanyProfileSerializer, LocationSerializer, SavedJobSerializer
from api.permissions import IsRecruiter, IsAdmin
from .filters import JobFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from elasticsearch_dsl import Q
from django.core.cache import cache
from hashlib import sha256

class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRecruiter()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_recruiter():
                return Job.objects.filter(company__owner=user)
            elif user.is_admin():
                return Job.objects.filter(status='pending')
        return Job.objects.filter(status='approved')

    def perform_create(self, serializer):
        company = self.request.user.company_profile
        serializer.save(company=company)


class CompanyProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsRecruiter]
    queryset = CompanyProfile.objects.all()

    def get_queryset(self):
        return CompanyProfile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]


class SavedJobViewSet(viewsets.ModelViewSet):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        job_id = self.request.data.get('job')
        job = get_object_or_404(Job, id=job_id)
        serializer.save(user=self.request.user, job=job)

    @action(detail=True, methods=['delete'], url_path='unsave')
    def unsave_job(self, request, pk=None):
        job = get_object_or_404(Job, id=pk)
        saved = SavedJob.objects.filter(user=request.user, job=job).first()
        if saved:
            saved.delete()
            return Response(status=204)
        return Response({"detail": "Not saved."}, status=400)



class JobSearchView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return Response({"results": [], "suggestions": []})

        # Create unique cache key
        cache_key = f"job-search:{sha256(query.encode()).hexdigest()}"

        # Try fetching from cache
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)  # ✅ FAST: response served from Redis

        # No cache hit, run ES queries
        main_query = Q("multi_match", query=query, fields=["title^3", "description"], fuzziness="AUTO") | \
                     Q("match_phrase_prefix", title={"query": query, "boost": 2})

        search = JobDocument.search().query(main_query)
        results = search[:10].execute()

        suggest_response = JobDocument.search().suggest(
            "job-suggest", query,
            completion={"field": "suggest", "fuzzy": {"fuzziness": 2}}
        ).execute()

        suggestions = []
        if hasattr(suggest_response, "suggest") and suggest_response.suggest:
            try:
                suggest_options = suggest_response.suggest["job-suggest"][0].options
                suggestions = [opt.text for opt in suggest_options]
            except (KeyError, IndexError, AttributeError, TypeError):
                suggestions = []

        response_data = {
            "results": [hit.to_dict() for hit in results],
            "suggestions": suggestions
        }

        # Cache the response for future queries
        cache.set(cache_key, response_data, timeout=60 * 5)

        return Response(response_data)