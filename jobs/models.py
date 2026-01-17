from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class JobField(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Job(models.Model):
  class JobStatusChoices(models.TextChoices):
    active = "AC", "ACTIVE"
    expired = "EX", "EXPIRED"
    deleted = "DL", "DELETED"

  title = models.CharField(max_length=300)
  company = models.CharField(max_length=300)
  location = models.CharField(max_length=500)

  url = models.URLField(unique=True)
  posted_at = models.CharField(max_length=100, null=True, blank=True)

  source = models.CharField(max_length=100)
  person_posted = models.CharField(max_length=200, null=True, blank=True)

  job_field = models.ForeignKey(JobField, on_delete=models.PROTECT)
  tags = models.ManyToManyField(Tag,blank=True)

  job_type = models.CharField(max_length=100, null=True, blank=True)
  salary = models.CharField(max_length=100, null=True, blank=True)

  external_id = models.CharField(max_length=200, null=True, blank=True)
  content_hash = models.CharField(max_length=64, null=True, blank=True)
  ingested_at = models.DateTimeField(auto_now_add=True)
  last_seen = models.DateTimeField(auto_now=True, db_index=True)

  status = models.CharField(
      max_length=2, 
      choices=JobStatusChoices.choices, 
      default=JobStatusChoices.active
  )

  class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["source", "external_id"],
            condition=~models.Q(external_id=None),
            name="unique_job_per_source"
    )
    ]   

    indexes = [
        models.Index(fields=["status"]),
        models.Index(fields=["ingested_at"]),
        models.Index(fields=["status", "-ingested_at"]),
        models.Index(fields=["last_seen"]),
    ]



  
