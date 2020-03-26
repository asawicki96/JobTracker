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
from django.db.models import QuerySet

'''Class responsible for collecting, filtering and saving data from Joobe REST API.
    Constructor takes one argument which is Tracker object.'''

class JoobleCollector(object):
    def __init__(self, tracker: Tracker = None):
        self.tracker = tracker
        if self.tracker:
            self.size = tracker.size
        self.offers = None
        self.latest = None
        self.json_data = None
        self.filtered_job_list = None

    """ Main method downloading, filtering and saving data, managed to be used
        when new Tracker is created or existing Tracker object is being edited."""

    def collect_jobs(self) -> None:
        self.latest = self.set_latest()
        self.json_data = self.get_json_data()
        self.filtered_job_list = self.filter()
        self.save_jobs(self.filtered_job_list)

    """ Downloading, filtering and saving data used to update offers when
        there are some in database"""

    def update_jobs(self) -> None:
        self.offers = self.get_queryset()
        self.latest = self.set_latest()
        self.json_data = self.get_json_data()
        self.filtered_job_list = self.filter()
        self.save_jobs(self.filtered_job_list)
        if self.filtered_job_list:
            self.delete_eldest_jobs()

    """ Get latest job by attr: updated """

    def get_latest_by_updated_job(self) -> Offer:
        try:
            latest_job = Offer.objects.filter(owner=self.tracker).latest('updated')
        except Exception as e:
            print(e)
        
        return latest_job

    """ Returns datetime object as date of latest offer,
         when it exists in db, or month ago"""

    def set_latest(self) -> datetime:
        latest_job = self.get_latest_by_updated_job()
        if latest_job:
            latest = latest_job.updated
            latest.replace(tzinfo=timezone.utc)
        else:
            now = timezone.now()
            latest = (now + timedelta(days=-30))
            latest.replace(tzinfo=timezone.utc)

        return latest

    """ Returns queryset object of all offers belonging to self.tracker object"""

    def get_queryset(self) -> QuerySet:
        try:
            offers = Offer.objects.filter(owner=self.tracker)
        except Exception as e:
            print(e)
        return offers

    """ Returns latest by order attr Offer object """

    def get_latest_by_order_job(self) -> Offer:
        try:
            latest_job = Offer.objects.filter(owner=self.tracker).latest('order')
        except ObjectDoesNotExist:
            latest_job = None

        return latest_job

    """ Returns sorted by 'updated' attr, 
        list of discts being offers, without duplications """

    def get_json_data(self) -> list:
        query = {}
        page = 1

        query['keywords'] = self.tracker.keywords
        if self.tracker.location:
            query['location'] = self.tracker.location
        if self.tracker.radius:
            query['radius'] = self.tracker.radius
        if self.tracker.salary:
            query['salary'] = self.tracker.salary

        query['page'] = page
        job_list = []
        periods = self.size//20 + 2

        for period in range(periods):
            jobs = get_jooble_jobs(query)['jobs']

            for job in jobs:
                if job not in job_list:
                    job_list.append(job)
            query['page'] = page + 1

        job_list = list({obj['id']: obj for obj in job_list}.values())
        job_list = sorted(job_list, key=itemgetter('updated'))
         
        return job_list

    """ Returns filtered list of offers without elder than the latest one in db
         and offers already stored in db""" 

    def filter(self) -> list:
        job_list = self.json_data.copy()

        for job in reversed(job_list):
            updated = self.parse_date(job['updated'])
            if updated <= self.latest:
                job_list = job_list[(job_list.index(job)):]
                break

        if self.offers:
            stored_ids = self.offers.values_list('foreign_identity')
            stored_ids = [ i[0] for i in stored_ids ]

            for job in job_list:
                f_id = job['id']
                if f_id in stored_ids:
                    job_list.remove(job)
         
        return job_list

    """ Saves Offer objects in db when given list of dicts containing offers"""

    def save_jobs(self, jobs: list) -> None:
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

    """ Delete eldest Offer objects wchich are not in range of tracker size """

    def delete_eldest_jobs(self) -> None:
        latest_job = self.get_latest_by_order_job()
        if latest_job:
            latest = latest_job.order
        oversize = latest - self.size + 1
        eldest = Offer.objects.filter(owner=self.tracker, order__lt=oversize)

        for obj in eldest:
            obj.delete()


    """ Returns aware datetime object when given date string in ISO 8601 """

    def parse_date(self, date: str) -> datetime:
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
    

