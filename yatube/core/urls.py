from django.urls import path
from django.conf import settings

from . import views

app_name = 'core'

urlpatterns = [
]

if settings.DEBUG:
    urlpatterns = [
        path('404/', views.page_not_found, name='404'),
        path('403/', views.csrf_failure, name='403'),
        path('500', views.error_code_500, name='500')
    ] + urlpatterns
