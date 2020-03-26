from django.urls import path
from . import views

app_name = 'offer'

urlpatterns = [
    path('<tracker_id>/list/', views.OfferListView.as_view(), name='offer_list'), 
    path('<tracker_id>/list/refresh/', views.OfferListRefresh.as_view(), name='refresh'),
]
