# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('summary_day', views.summary_day, name='summary_day'),
    path('summary_month', views.summary_month, name='summary_month'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
