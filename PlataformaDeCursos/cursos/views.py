from django.shortcuts import render, redirect, get_object_or_404
from .models import Curso, Inscripcion, Recurso, Progreso
from .forms import InscripcionForm, RecursoForm
from django.http import HttpResponseForbidden
from datetime import date
from .models import Curso

# Create your views here.

def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos/cursos.html', {'cursos': cursos})


def InscripcionACursos(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    
    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            inscripcion = form.save(commit=False)
            inscripcion.curso = curso
            inscripcion.save()
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = InscripcionForm()
    
    return render(request, 'cursos/inscripcion.html', {'form': form, 'curso': curso})

def SubidaDeMaterias(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)

    if request.method == 'POST':
        form = RecursoForm(request.POST)
        if form.is_valid():
            recurso = form.save(commit=False)
            recurso.curso = curso
            recurso.save()
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = RecursoForm()

    return render(request, 'cursos/subir_materia.html', {'form': form, 'curso': curso})

def ProgresoDelEstudiante(request, inscripcion_id):
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_id)
    curso = inscripcion.curso
    recursos = Recurso.objects.filter(curso=curso)
    progreso_existente = {p.recurso.id: p for p in Progreso.objects.filter(inscripcion=inscripcion)}

    if request.method == 'POST':
        recurso_id = request.POST.get('recurso_id')
        completado = request.POST.get('completado') == 'on'
        recurso = get_object_or_404(Recurso, pk=recurso_id)

        progreso, creado = Progreso.objects.get_or_create(inscripcion=inscripcion, recurso=recurso)
        progreso.completado = completado
        progreso.fecha_completado = date.today() if completado else None
        progreso.save()

        return redirect('progreso_estudiante', inscripcion_id=inscripcion_id)

    contexto = {
        'inscripcion': inscripcion,
        'recursos': recursos,
        'progreso_existente': progreso_existente,
    }

    return render(request, 'cursos/progreso_estudiante.html', contexto)
