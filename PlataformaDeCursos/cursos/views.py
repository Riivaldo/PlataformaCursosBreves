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
        
    #Arreglando pequeño error en la urls
    curso = get_object_or_404(Curso, id=curso_id)
    return render(request, 'cursos/subir_material_extra.html', {'form': form, 'curso': curso})


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


# TERCERA FUNCIONALIDAD IMPLEMENTADA
# progreso del estudiante.
@login_required
def progreso_estudiante(request):
    usuario = request.user
    inscripciones = Inscripcion.objects.filter(user=usuario)

    progreso_por_curso = {}

    for inscripcion in inscripciones:
        curso = inscripcion.curso
        recursos = Recurso.objects.filter(curso=curso)
        total = recursos.count()

        progresos = Progreso.objects.filter(
            inscripcion=inscripcion,
            completado=True
        )
        completados_ids = set(progresos.values_list('recurso_id', flat=True))
        completados_count = len(completados_ids)
        
        #calcula el porcentaje del progreso
        porcentaje = (completados_count / total * 100) if total > 0 else 0
        progreso_por_curso[curso.id] = {
            'curso': curso,
            'porcentaje': round(porcentaje, 2),
            'total': total,
            'completados': completados_count,
            'recursos': recursos,
            'completados_ids': completados_ids
        }
    return render(request, 'cursos/progreso_estudiante.html', {
        'progreso_por_curso': progreso_por_curso
    })


# Ver un recurso
@login_required
def ver_recurso(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id)
    inscripcion = Inscripcion.objects.filter(user=request.user, curso=recurso.curso).first()
    if not inscripcion:
        return HttpResponseForbidden("No estás inscrito en este curso.")

    progreso = Progreso.objects.filter(inscripcion=inscripcion, recurso=recurso).first()
    
    completado = progreso.completado if progreso else False
    return render(request, 'cursos/ver_recurso.html', {
        'recurso': recurso,
        'completado': completado
    })

# Marcar como completado el recurso visto por el estudiante.
@login_required
def marcar_completado(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id)
    inscripcion = Inscripcion.objects.filter(user=request.user, curso=recurso.curso).first()
    if not inscripcion:
        return HttpResponseForbidden("No estás inscrito en este curso.")

    progreso, _ = Progreso.objects.get_or_create(inscripcion=inscripcion, recurso=recurso)
    progreso.completado = True
    progreso.fecha_completado = date.today()
    progreso.save()

    return redirect('ver_recurso', recurso_id=recurso.id)

