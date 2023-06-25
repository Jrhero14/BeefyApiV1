from django.contrib import admin
from django.urls import path

from BeefyRest.urls import api
from BeefyRest.views import index

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('api/', api.urls, name='Endpoints')
]
