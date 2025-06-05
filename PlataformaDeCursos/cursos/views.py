from django.shortcuts import render
from django.shortcuts import render
from .models import Curso

# Create your views here.

def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos/cursos.html', {'cursos': cursos})