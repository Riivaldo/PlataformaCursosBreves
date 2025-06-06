from django.shortcuts import render, redirect, get_object_or_404
from .models import Curso, Inscripcion, Recurso, Progreso
from .forms import InscripcionForm, RegistroUsuarioForm
from django.http import HttpResponseForbidden
from datetime import date
from .models import Curso , Inscripcion, MaterialExtra
from .forms import InscripcionForm, MaterialExtraForm
from django.shortcuts import render, get_object_or_404
from .models import Curso
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Create your views here.
# Lista de los cursos en la pagina principal
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos/cursos.html', {'cursos': cursos})


# muesta a detalles las fehas de inicio y fin como tambien los usuarios inscritos en cada curso

def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripciones = Inscripcion.objects.filter(curso=curso)
    return render(request, 'cursos/detalle_Cursos.html', {
        'curso': curso,
        'inscripciones': inscripciones
    })
# PRIMER FUNCIONALIDAD IMPLEMENTADA
# Inscripción de un usuario a un curso
# requiriendo el login del usuario
@login_required
def inscribirse_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    user = request.user

    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            inscripcion, created = Inscripcion.objects.get_or_create(
                user=user,
                curso=curso,
                defaults={
                    'nombre_estudiante': form.cleaned_data['nombre_estudiante'],
                    'email_estudiante': form.cleaned_data['email_estudiante'],
                }
            )
            if not created:
                # Si ya existe manda este mensaje de error
                form.add_error(None, 'Ya estás inscrito en este curso.')
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = InscripcionForm(initial={
            'nombre_estudiante': user.get_full_name() or user.username,
            'email_estudiante': user.email
        })

    return render(request, 'cursos/inscribirse_curso.html', {
        'curso': curso,
        'form': form
    })
#subir material extra a un curso
@login_required
def subir_material_extra(request, curso_id):
    if request.method == 'POST':
        form = MaterialExtraForm(request.POST, request.FILES)
        if form.is_valid():
            material_extra = form.save(commit=False)
            material_extra.usuario = request.user
            material_extra.curso_id = curso_id
            material_extra.save()
            return redirect('detalle_curso', pk=curso_id)
    else:
        form = MaterialExtraForm()
    return render(request, 'subir_material_extra.html', {'form': form})

#  VISTA PARA QUE CUALQUIER USUARIO SE PUEDA INSCRIBIR A UN CURSO
def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_cursos')
    else:
        form = RegistroUsuarioForm()
    return render(request, "registration/registro.html", {"form": form})
