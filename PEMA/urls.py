from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    #path(
    #    route='',
    #    view=views.IndexView.as_view(),
    #    name='index'
    #),
    #path(
    #    route='test/',
    #    name='test',
    #    view=views.test
    #),
    path(
        'accounts/', include('django.contrib.auth.urls')
    ),
    path(
        '', TemplateView.as_view(template_name='index.html'), name='index'
    ),
    
]