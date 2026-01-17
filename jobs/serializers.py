from rest_framework import serializers

class JobInputSerializer(serializers.Serializer):
    title = serializers.CharField()
    company = serializers.CharField()
    location = serializers.CharField(required=False, allow_blank=True)
    url = serializers.URLField()
    posted_at = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField()
    person_posted = serializers.CharField(
      required=False,
      allow_blank=True
    )
    external_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    job_field = serializers.CharField()
    salary = serializers.CharField(required=False, allow_blank=True)
    job_type = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
      child=serializers.CharField(),
      required=False
    )
