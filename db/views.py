from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
from django import forms
import django_excel as excel
from .models import *
from .filters import LocationFilter, DataFilter
import csv
#from django.contrib import messages


def home(request):

    d=Data.objects.all()




    filter1=DataFilter(request.GET, queryset=d)
    d=filter1.qs


    context={
        #'locations':locations,'metrics':metrics,
        'filter':filter1,
        'd': d,



             }

    return render(request, 'home.html',context)
    #



class UploadFileForm(forms.Form):
    file = forms.FileField()


def upload_data(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        def data_func(row):
            location = Location.objects.get_or_create(name=row[0])[0]
            row[0]=location
            metric = Metric.objects.get_or_create(name=row[1])[0]
            row[1]=metric
            unit = Unit.objects.get_or_create(name=row[2])[0]
            row[2]=unit

            source = Source.objects.get_or_create(name=row[3])[0]
            row[3]=source
            return row

        if form.is_valid():
            request.FILES["file"].save_to_database(
                model=Data,
                initializer=data_func,
                mapdict = {"Location": "location", "Metric": "metric", "Unit": "unit", "Source": "source",
                     "Value": "value", "Start": "start", "End": "end", "Type": 'datatype'}

            )
        #     return redirect("handson_view")
        # else:
        #     return HttpResponseBadRequest()

    else:
        form = UploadFileForm()
    return render(
        request,
        "data_upload.html",
        {
            "form": form,
            "title": "Import excel data into database example",
            "header": "Please upload sample-data.xls:",
        },
    )