from django.urls import path
from . import views

urlpatterns = [
    # path('', views.vistaInicial, name='inicio'),
    # vista inicial, tabla de cursos
    path('', views.lista_cursos, name='lista_cursos'),
    # vista de detalle de cada curso
    path("curso/<int:curso_id>/", views.detalle_curso, name="detalle_curso"),
    # vista para la inscripción a un curso
    path('curso/<int:curso_id>/inscribirse/', views.inscribirse_curso, name='inscribirse_curso'),

]
