from django.urls import path
from . import views
urlpatterns = [
    # path('', views.vistaInicial, name='inicio'),
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('curso/<int:curso_id>/inscribirse/', views.InscripcionACursos, name='inscripcion_curso'),
    path('curso/<int:curso_id>/subir/', views.SubidaDeMaterias, name='subida_materias'),
    path('inscripcion/<int:inscripcion_id>/progreso/', views.ProgresoDelEstudiante, name='progreso_estudiante'),
]
