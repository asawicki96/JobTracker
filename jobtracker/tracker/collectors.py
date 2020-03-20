from .models import Tracker
from offer.models import Offer
from .api_connection import get_jooble_jobs
from operator import itemgetter
from django.core.exceptions import ObjectDoesNotExist
from dateutil import parser , relativedelta
from datetime import datetime , timedelta
from django.utils import timezone
import pytz
from django.conf import settings


class JoobleCollector(object):
    def __init__(self, tracker: object):
        self.tracker = tracker
        self.size = tracker.size
        self.offers = None
        self.latest = None
        self.json_data = None
        self.filtered_job_list = None

    def collect_jobs(self):
        self.latest = self.set_latest()
        self.json_data = self.get_json_data()
        self.save_jobs(self.json_data)

    def update_jobs(self):
        self.offers = self.get_queryset()
        self.latest = self.set_latest()
        self.json_data = self.get_json_data()
        self.filtered_job_list = self.filter()
        self.save_jobs(self.filtered_job_list)
        self.delete_eldest_jobs()


    def set_latest(self):
        try:
            latest = Offer.objects.filter(owner=self.tracker).latest('updated')
            latest = latest.updated
            latest.replace(tzinfo=timezone.utc)
        except:
            now = timezone.now()
            latest = now + timedelta(days=-30)
            latest.replace(tzinfo=timezone.utc)
        return latest

    def get_queryset(self):
        try:
            offers = Offer.objects.filter(owner=self.tracker)
        except Exception as e:
            print(e)
        return offers

    def get_latest_job(self):
        try:
            latest_job = Offer.objects.filter(owner=self.tracker).latest('order')
        except ObjectDoesNotExist:
            latest_job = None

        return latest_job

    def get_json_data(self):
        query = {}
        page = 1

        query['keywords'] = self.tracker.keywords
        if self.tracker.location:
            query['location'] = self.tracker.location
        if self.tracker.radius:
            query['radius'] = str(self.tracker.radius)
        if self.tracker.salary:
            query['salary'] = str(self.tracker.salary)

        query['page'] = str(page)
        job_list = []
        periods = self.size//20 + 2

        for period in range(periods):
            jobs = get_jooble_jobs(query)['jobs']

            for job in jobs:
                if job not in job_list:
                    job_list.append(job)
            query['page'] = str(page + 1)

        job_list = list({obj['id']: obj for obj in job_list}.values())
        job_list = sorted(job_list, key=itemgetter('updated'))
            
        return job_list


    def filter(self):
        stored_ids = self.offers.values_list('foreign_identity')
        stored_ids = [ i[0] for i in stored_ids ]
        
        job_list = self.json_data.copy()

        for job in job_list:
            updated = self.parse_date(job['updated'])
        
            if updated <= self.latest:
                job_list = job_list[:(job_list.index(job))]
                break
        
        for job in job_list:
            f_id = job['id']
            if f_id in stored_ids:
                job_list.remove(job)
        
        return job_list

    def save_jobs(self, jobs: list):
        for job in jobs:
            if not 'company' in job.keys():
                company = None
            else:
                company = job['company']

            offer = Offer(  owner = self.tracker,
                            foreign_identity = job['id'],
                            title = job['title'],
                            location = job['location'],
                            snippet = job['snippet'],
                            salary = job['salary'],
                            source = job['source'],
                            job_type = job['type'],
                            link = job['link'],
                            company = company,
                            updated = parser.parse(job['updated'])
                        )
            offer.save()

    def delete_eldest_jobs(self):
        latest_job = self.get_latest_job()
        if latest_job:
            latest = latest_job.order
        oversize = latest - self.size + 1
        eldest = Offer.objects.filter(owner=self.tracker, order__lt=oversize)
        for obj in eldest:
            obj.delete()

    def parse_date(self, date: str):
        date_vals = date.split("T")[0]
        date_vals = date_vals.split("-")

        time_vals = date.split("T")[1]
        time_vals = time_vals.split(":")
        time_vals[2] = time_vals[2].split(".")[0]
        microseconds = date.split(".")[1]


        if "+" in microseconds:
            microseconds = microseconds[:6]
        if len(microseconds) > 6:
            microseconds = microseconds[:6]

        multiplier = 1
        ms_val = 0
        for i in range(1, 6):
            ms_val = ms_val + int(microseconds[-i]) * multiplier
            multiplier = multiplier * 10

        return datetime(
                        year=int(date_vals[0]),
                        month=int(date_vals[1]),
                        day=int(date_vals[2]),
                        hour=int(time_vals[0]),
                        minute=int(time_vals[1]),
                        second=int(time_vals[2]),
                        microsecond=ms_val,
                        tzinfo=timezone.utc
                        )
    

