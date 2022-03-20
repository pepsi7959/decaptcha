from django.urls import path

from . import views

urlpatterns = [
    path('decaptcha', views.decaptcha, name='decaptcha'),
    path('feedback', views.feedback, name='feedback'),
]
