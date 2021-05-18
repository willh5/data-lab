from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='datalab-home'),
    path('upload/', views.upload_data, name='upload data'),


]