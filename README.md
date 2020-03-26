# JobTracker

An application which allows users subscription of job offers posted on Jooble.com.

Application uses https://pl.jooble.org/api/about API server for offers data. API provides searching by keywords, location etc...
Users can set up a periodically repeated query and view found jobs. Automatic checks are made by means Celery periodic tasks,
each day at 00:03 o'clock. Program collect offers not older than 30 days at tracker(query) creation and updates data daily.
Every second day it sends email containing new found offers to user. New offers are filtered by publish date (only newer
than the newest stored in db) and by 'id' (to prevent storing offer duplicates). Each tracker has offer lmit equal to 50.
After every update the eldest jobs out of limit are deleted. New offers are stored in REDIS db as a list of dictionaries until
they are sent to tracker's owner. Then whole list is deleted and new period begins.

Steps to setup application:

- register on https://pl.jooble.org/api/about and get your API key,
- make virtual environment and install all dependencies listed in Pipfile,
- setup environment variables in your virtual environment as follows:
   JOOBLE_API_KEY='your api key';
   EMAIL_HOST='your email host';
   EMAIL_HOST_USER='your email user';
   EMAIL_HOST_PASSWORD='your email password';
   EMAIL_PORT= your email port default: 587;
- migrate db,
- create superuser,
- migrate celery tables,
- run redis server,
- start celery worker by typing ->  celery -A proj worker -B,
- run Django development server,
- register and add new tracker,
- now you can track your job.

Default localhost sites:

- localhost:8000/accounts/ -> dashboard for authenticated user with list of user's existing trackers 
- localhost:8000/accounts/edit/ -> page with account edition form
- localhost:8000/tracker/create/ -> page with tracker creation form 
- localhost:8000/tracker/<id>/ -> page with tracker edition form 
- localhost:8000/offer/<tracker_id>/list/ -> page with list of offers belonging to tracker
- localhost:8000/accounts/login/ -> login site
- localhost:8000/accounts/register/ -> register site




