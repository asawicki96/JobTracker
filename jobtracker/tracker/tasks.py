from celery import task
from .collectors import JoobleCollector
from django.conf import settings
from .models import Tracker
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template

import redis
import json


r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


""" Updates offers of all Tracker objects """

@task
def update_all_trackers():
    trackers = Tracker.objects.all().values('id')
    for tracker in trackers:
        update_jobs(tracker['id'])

""" Collects offers when tracker.id given """

@task
def collect_jobs(tracker_id: int):
        tracker = Tracker.objects.get(id=tracker_id)
        collector = JoobleCollector(tracker)
        collector.collect_jobs()

""" Updates offers when tracker.id given. 
    Appends as new offers to list stored in REDIS DB"""

@task
def update_jobs(tracker_id: int):
        tracker = Tracker.objects.get(id=tracker_id)
        collector = JoobleCollector(tracker)
        collector.update_jobs()

        new_jobs = collector.filtered_job_list

        if len(new_jobs) > 0:
            for job in new_jobs:
                json_job = json.dumps(job)
                r.lpush('tracker:{}:new_offers'.format(tracker.id), json_job)
    

""" Sends mails to all Tracker objects owners """

@task
def send_mails():
    trackers = Tracker.objects.all().values('id')
    for tracker in trackers:
        send_mail(tracker['id'])
    
""" Sends mail to Tracker object owner containing all new offers, when tracker.id given. 
    Delete all new offers in REDIS DB, belonging to Tracker object"""

def send_mail(tracker_id: int):
    new_jobs_json = r.lrange(name='tracker:{}:new_offers'.format(tracker_id), start=-100, end=100)
    new_jobs = []
    if new_jobs_json:
        for job in new_jobs_json:
            job_obj = json.loads(job)
            new_jobs.append(job_obj)
    
    if new_jobs:
        tracker = Tracker.objects.get(id=tracker_id)
        user_email = tracker.owner.email
        
        subject = 'Tracker: {}'.format(tracker.keywords)
        html_content = get_template('tracker/email_job_list.html').render({'new_jobs': new_jobs})
        from_email = 'jobtracker@gmail.com'
        to = tracker.owner.email
       
        msg = EmailMessage(subject, html_content, from_email, [to])
        msg.content_subtype = "html"
        try:
            msg.send()
        except Exception as e:
            print(e)

        r.delete('tracker:{}:new_offers'.format(tracker_id))