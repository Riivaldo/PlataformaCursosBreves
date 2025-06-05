from django import forms
from .models import Inscripcion, Recurso

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['nombre_estudiante', 'email_estudiante']

class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ['titulo', 'descripcion', 'tipo_archivo', 'enlace']

