from django import forms
from .models import Inscripcion , MaterialExtra
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Inscripcion
#   FORMULARIO PARA LA INSCRIPCION DE UN USUARIO A UN CURSO X
class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['nombre_estudiante', 'email_estudiante']
# material extra para los cursos
class MaterialExtraForm(forms.ModelForm):
    class Meta:
        model = MaterialExtra
        fields = ('archivo', 'descripcion')
# REGISTRO PARA QUE CUALQUIER USUARIIO PUEDA CREAR UNA CUENTA E INSCRIBIRSE A UN CURSO
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")