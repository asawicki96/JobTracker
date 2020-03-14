from django.urls import path
from . import views


app_name = 'trakcer'

urlpatterns = [
    path('<int:tracker_id>/', views.TrackerEditView.as_view(), name='tracker_detail'),
]
