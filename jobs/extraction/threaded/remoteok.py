import requests
from jobs.extraction.base import BaseExtractor

class RemoteOkExtractor(BaseExtractor):
    source = "remoteok"

    def run(self) -> list[dict]:
        url = "https://remoteok.io/api"
        response = requests.get(
            url, 
            timeout=15,
            headers={"User-Agent": "JobPlatformBot/1.0"}
        )
        response.raise_for_status()
        data = response.json()

        jobs = []
        for item in data[1:]: # Skip the first item which is metadata
            if not isinstance(item, dict):
                continue
            tags = item.get("tags") or []
            job = {
                "title": item.get("position"),
                "company": item.get("company"),
                "location": item.get("location", ""),
                "url": item.get("url"),
                "posted_at_raw": item.get("date"),
                "source": self.source,
                "external_id": str(item.get("id")),
                "job_field":  (
                    tags[0].title()
                    if tags and isinstance(tags[0], str)
                    else "Uncategorized"
                ),
                "salary": item.get("salary"),
                "job_type": None,
                "tags": tags,
            }
            jobs.append(job)

        return jobs
