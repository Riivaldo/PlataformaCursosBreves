from django.urls import path
from . import views
urlpatterns = [
    # path('', views.vistaInicial, name='inicio'),
    path('cursos/', views.lista_cursos, name='lista_cursos'),
]
