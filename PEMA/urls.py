from django.urls import path
from . import views

urlpatterns = [
    path(
        route='test/',
        name='test',
        view=views.test
    ),
]