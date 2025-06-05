from django import forms
from .models import Inscripcion
#   FORMULARIO PARA LA INSCRIPCION DE UN USUARIO A UN CURSO X
class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['nombre_estudiante', 'email_estudiante']

