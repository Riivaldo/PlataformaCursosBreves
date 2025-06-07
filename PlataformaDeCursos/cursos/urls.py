from django.urls import path
from cursos.views import login_redirect
from . import views

urlpatterns = [
    # path('', views.vistaInicial, name='inicio'),
    # vista inicial, tabla de cursos
    path('', views.lista_cursos, name='lista_cursos'),
    # vista de detalle de cada curso
    path("curso/<int:curso_id>/", views.detalle_curso, name="detalle_curso"),
    # vista para la inscripción a un curso
    path('curso/<int:curso_id>/inscribirse/', views.inscribirse_curso, name='inscribirse_curso'),
     # vista para el registro de un usuario
    path('registro/', views.registro_usuario, name='registro_usuario'), 
    # vista para subir material extra a un curso
    path('curso/<int:curso_id>/subir_material_extra/', views.subir_material_extra, name='subir_material_extra'),
    # vista del progreso de todos los cursos
    path('progreso/', views.progreso_estudiante, name='progreso_estudiante'),
    # vista para ver el recurso
    path('recurso/<int:recurso_id>/', views.ver_recurso, name='ver_recurso'),
    # vista para ver el recurso "completar"
    path('recurso/<int:recurso_id>/completar/', views.marcar_completado, name='marcar_completado'),
    # vista para ver el maestro"
    path('dashboard/', views.dashboard, name='dashboard'),
    # vista para la redireccion entre estudiante y maestro"
    path('redireccion/', login_redirect, name='login_redirect'),
]



