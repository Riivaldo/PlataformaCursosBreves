from django.contrib import admin
from .models import Profesor, Curso, Inscripcion, Recurso, Progreso
# Register your models here.
admin.site.register(Profesor)
admin.site.register(Curso)
admin.site.register(Inscripcion)
admin.site.register(Recurso)
admin.site.register(Progreso)
