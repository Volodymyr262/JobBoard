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
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
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


class JobSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class JobSearchView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        if not query:
            return Response({
                "results": [],
                "suggestions": [],
                "count": 0,
                "next": None,
                "previous": None
            })

        cache_key = f"job-search:{sha256(f'{query}:{page}:{page_size}'.encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Build ES query
        main_query = (
            Q("multi_match", query=query, fields=["title^3", "description"], fuzziness="AUTO") |
            Q("match_phrase_prefix", title={"query": query, "boost": 2})
        )

        search = JobDocument.search().query(main_query)

        # Count total results
        total = search.count()

        # Apply pagination (Elasticsearch slicing)
        start = (page - 1) * page_size
        end = start + page_size
        results = search[start:end].execute()

        # Suggestions
        suggest_response = JobDocument.search().suggest(
            "job-suggest", query,
            completion={"field": "suggest", "fuzzy": {"fuzziness": 2}}
        ).execute()

        suggestions = (
            [opt.text for opt in suggest_response.suggest["job-suggest"][0].options]
            if hasattr(suggest_response, "suggest") and "job-suggest" in suggest_response.suggest
            else []
        )

        # Build paginated response manually
        next_page = request.build_absolute_uri(f"?q={query}&page={page+1}&page_size={page_size}") if end < total else None
        prev_page = request.build_absolute_uri(f"?q={query}&page={page-1}&page_size={page_size}") if page > 1 else None

        response_data = {
            "count": total,
            "next": next_page,
            "previous": prev_page,
            "results": [hit.to_dict() for hit in results],
            "suggestions": suggestions,
        }

        # Cache result
        cache.set(cache_key, response_data, timeout=60 * 5)
        return Response(response_data)