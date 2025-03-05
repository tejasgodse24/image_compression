
from django.urls import path
from imgcompress.views import *
urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('webhook/', webhook_reciever, name="webhook_reciever"),
    path('status/<request_id>/', check_status, name="check_status"),
]
