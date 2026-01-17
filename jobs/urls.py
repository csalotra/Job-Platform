from django.urls import path
from jobs.api import IngestJobs

urlpatterns = [
    path('ingest/', IngestJobs.as_view(), name="ingest-jobs"),
]
