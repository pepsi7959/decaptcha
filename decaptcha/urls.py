from django.urls import path

from . import views

urlpatterns = [
    path('decaptcha', views.decaptcha, name='decaptcha'),
    path('feedback', views.feedback, name='feedback'),
    path('get_train_image', views.get_train_image, name='get_train_image'),
]
