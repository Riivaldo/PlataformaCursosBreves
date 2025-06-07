from django.shortcuts import render, redirect, get_object_or_404
from .models import Curso, Inscripcion, MaterialExtra, Recurso, Progreso
from .forms import InscripcionForm, RegistroUsuarioForm, MaterialExtraForm
from .forms import InscripcionForm, RegistroUsuarioForm
from django.http import HttpResponseForbidden
from datetime import date
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Create your views here.
# Verifica si el usuario tiene asociado un profesor para inicio de Sesion y redirecciones
@login_required
def login_redirect(request):
    if hasattr(request.user, 'profesor'):
        return redirect('dashboard')
    else:
        return redirect('lista_cursos')

@login_required
def dashboard(request):
    if hasattr(request.user, 'profesor'):
        profesor = request.user.profesor
        cursos = Curso.objects.filter(profesor=profesor)
        return render(request, 'cursos/dashboard_profesor.html', {'cursos': cursos})
    else:
        return redirect('cursos/cursos.html') 
    
# Lista de los cursos en la pagina principal
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos/cursos.html', {'cursos': cursos})


# muesta a detalles las fehas de inicio y fin como tambien los usuarios inscritos en cada curso

@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripciones = Inscripcion.objects.filter(curso=curso)
    es_profesor = hasattr(request.user, 'profesor')  # <-- NUEVA LÍNEA

    return render(request, 'cursos/detalle_Cursos.html', {
        'curso': curso,
        'inscripciones': inscripciones,
        'es_profesor': es_profesor 
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
    
# SEGUNDA FUNCIONALIDAD IMPLEMENTADA
# SUBIR UN MATERIAL EXTRA
# requiriendo el loggin solo del maestro encargado de la materia

@login_required
def subir_material_extra(request, curso_id):
    if request.method == 'POST':
        form = MaterialExtraForm(request.POST, request.FILES)
        if form.is_valid():
            material_extra = form.save(commit=False)
            material_extra.usuario = request.user
            material_extra.curso_id = curso_id
            material_extra.save()
            return redirect('detalle_curso', curso_id=curso_id)
    else:
        form = MaterialExtraForm()
        
    #Arreglando pequeño error en la urls
    curso = get_object_or_404(Curso, id=curso_id)
    return render(request, 'cursos/subir_material_extra.html', {'form': form, 'curso': curso})


#  VISTA PARA QUE CUALQUIER USUARIO SE PUEDA INSCRIBIR A UN CURSO (evitar al maestro) 
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
# permite al estudiante completar recursos de materias inscritas y verlos en tiempo real
@login_required
def progreso_estudiante(request):
    usuario = request.user
    inscripciones = Inscripcion.objects.filter(user=usuario)
    
    progresos = Progreso.objects.filter(inscripcion__in=inscripciones).select_related('recurso', 'inscripcion', 'inscripcion__curso')

    progreso_por_curso = {}
    for inscripcion in inscripciones:
        recursos = Recurso.objects.filter(curso=inscripcion.curso)
        completados = progresos.filter(inscripcion=inscripcion, completado=True).count()
        total = recursos.count()
        porcentaje = (completados / total * 100) if total > 0 else 0
        progreso_por_curso[inscripcion.curso] = {
            'porcentaje': round(porcentaje, 2),
            'total': total,
            'completados': completados,
            'recursos': recursos
        }

    return render(request, 'cursos/progreso_estudiante.html', {
        'progreso_por_curso': progreso_por_curso
    })

# Ver un recurso ya creado
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

