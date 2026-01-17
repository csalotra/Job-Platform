import hashlib
import logging
from django.db import transaction
from django.utils import timezone
from jobs.models import Job, JobField, Tag
from django.db import IntegrityError

logger = logging.getLogger(__name__)

def compute_hash(data):
    def norm(s):
        return (s or "").strip().lower().replace("  ", " ")

    key = "||".join([
        norm(data.get("title")),
        norm(data.get("company")),
        norm(data.get("location")),
        norm(data.get("salary")),
        norm(data.get("job_type")),
    ])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


@transaction.atomic
def ingest(job_dicts):
    """
    Returns stats to see what happened
    """
    stats = {
        "new": 0,
        "updated": 0,
        "seen": 0,
        "reactivated": 0,
        "skipped": 0,
        "errors": 0
    }

    # Deduplication check
    seen = set()
    unique_jobs = []

    for data in job_dicts:
        key = (data.get("source"), data.get("external_id"), data["url"])
        if key in seen:
            stats["skipped"] += 1
            continue
        seen.add(key)
        unique_jobs.append(data)

    for data in unique_jobs:
        try:
            action = _upsert_job(data)
            stats[action] += 1
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"Failed to ingest job {data.get('url')}: {e}", exc_info=True)

    return stats


def _upsert_job(data):
    now = timezone.now()
    new_hash = compute_hash(data)

    job = None
    if ext_id := data.get("external_id"):
        job = Job.objects.filter(source=data["source"], external_id=ext_id).first()

    if not job:
        job = Job.objects.filter(url=data["url"]).first()

    if job:
      update_fields = ["last_seen"]
      action = "seen"

      # Reactivation
      if job.status != Job.JobStatusChoices.active:
          job.status = Job.JobStatusChoices.active
          update_fields.append("status")
          action = "reactivated"

      # Content change detection
      if job.content_hash != new_hash:
          changed_content_fields = []
          for field in ["title", "company", "location", "salary", "job_type", "person_posted"]:
              new_value = data.get(field)
              if new_value is not None and getattr(job, field) != new_value:
                  setattr(job, field, new_value)
                  changed_content_fields.append(field)

          job.content_hash = new_hash
          update_fields.append("content_hash")
          update_fields.extend(changed_content_fields)

          if changed_content_fields:
              action = "updated" if action == "seen" else action

      job.last_seen = now
      job.save(update_fields=update_fields)
      return action

    # New job
    job_field_name = (data.get("job_field") or "Uncategorized").strip()
    job_field, _ = JobField.objects.get_or_create(name=job_field_name)

    try:
        job = Job.objects.create(
            title=data["title"],
            company=data["company"],
            location=data["location"],
            url=data["url"],
            posted_at = data.get("posted_at"),
            source=data["source"],
            external_id=data.get("external_id"),
            job_field=job_field,
            job_type=data.get("job_type"),
            salary=data.get("salary"),
            person_posted=data.get("person_posted"),
            content_hash=new_hash,
            ingested_at=now,
            last_seen=now,
            status=Job.JobStatusChoices.active,
        )
    except:
        job = Job.objects.get(
            source=data["source"],
            external_id=data.get("external_id")
        )
        return "seen"
    

    for tag_name in data.get("tags", []):
        clean_tag = tag_name.strip().lower()
        if clean_tag:
            tag, _ = Tag.objects.get_or_create(name=clean_tag)
            job.tags.add(tag)

    return "new"