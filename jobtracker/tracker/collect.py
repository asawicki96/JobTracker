from .models import Tracker
from offer.models import Offer
from .api_connection import get_jooble_jobs
from operator import itemgetter

def collect_jobs(tracker: object, size=50):
    query = {}
    page = 1
    stored = Offer.objects.filter(owner=tracker)
    stored_ids = []
    for obj in stored:
        stored_ids.append(int(obj.foreign_identity))

    #print(stored_ids)

    query['keywords'] = tracker.keywords
    if tracker.location:
        query['location'] = tracker.location
    if tracker.radius:
        query['radius'] = str(tracker.radius)
    if tracker.salary:
        query['salary'] = str(tracker.salary)
    
    query['page'] = str(page)
    job_list = []
    periods = size//20 + 1

    for period in range(periods):
        jobs = get_jooble_jobs(query)['jobs']

        for job in jobs:
            job_list.append(job)

        query['page'] = str(page+1)

    job_list.sort(key=itemgetter('updated'))
    
    for i in range(size):
        job = job_list[i]
        if job['id'] not in stored_ids:
            save_job(job=job_list[i], tracker=tracker)
    

def save_job(job: dict, tracker: object):
    if not 'company' in job.keys():
        company = None
    else:
        company = job['company']

    offer = Offer(  owner = tracker,
                    foreign_identity = job['id'],
                    title = job['title'],
                    location = job['location'],
                    snippet = job['snippet'],
                    salary = job['salary'],
                    source = job['source'],
                    job_type = job['type'],
                    link = job['link'],
                    company = company,
                    updated = job['updated']
                )
    offer.save()