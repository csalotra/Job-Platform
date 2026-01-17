from celery import shared_task
from jobs.ingestions.service import ingest
import logging
logger = logging.getLogger(__name__)

@shared_task(
  bind=True,
  autoretry_for=(Exception,),
  retry_kwargs={"max_retries": 3, "countdown": 60},
  retry_backoff=True          
)
def ingest_jobs_task(self, job_list):
      logger.info("Processing job chunk size=%s", len(job_list))
      return ingest(job_list)