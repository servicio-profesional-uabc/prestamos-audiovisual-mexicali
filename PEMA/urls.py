from django.urls import path
from . import views

urlpatterns = [
    path(
        route='',
        view=views.IndexView.as_view(),
        name='index'
    ),
    path(
        route='test/',
        view=views.test,
        name='test'
    ),

    path(
        route='prestatario.html',
        view=views.PrestatarioView.as_view(),
        name='prestatario_html'
    ),
    
    path(
        route='carrito.html',
        view=views.CarritoView.as_view(),
        name='carrito_html'
    ),
]
