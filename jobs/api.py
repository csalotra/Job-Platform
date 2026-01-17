from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jobs.tasks import ingest_jobs_task
from jobs.serializers import JobInputSerializer
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

class IngestJobs(APIView):
  authentication_classes =[]
  permission_classes =[]

  def post(self, request):
    batch_id = request.data.get("batch_id")
    raw_jobs = request.data.get("jobs")

    serializer = JobInputSerializer(data=raw_jobs, many=True)
    if not serializer.is_valid():
       return Response(serializer.errors, status=400)
    
    jobs = serializer.validated_data
    
    if not batch_id or not isinstance(jobs, list):
      return Response({"error":"expected list of jobs and batch_id"}, status=400)
    
    batch_key = f"batch:{batch_id}"
    if r.exists(batch_key):
       return Response({"status": "duplicate batch"}, status=200)
    
    r.setex(batch_key, 3600, "1")

    # Chunking the large list
    for chunk in chunked(jobs, 500):
       ingest_jobs_task.delay(chunk)

    return Response({"message": "Ingestion queued"}, status=status.HTTP_202_ACCEPTED)

