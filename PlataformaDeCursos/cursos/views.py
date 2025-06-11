from django.shortcuts import render, redirect, get_object_or_404
from .models import Profesor, Curso, Inscripcion, MaterialExtra, Recurso, Progreso
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
    es_profesor = hasattr(request.user, 'profesor')
    
    # verifica si  el usuario inscrito en este curso
    esta_inscrito = Inscripcion.objects.filter(user=request.user, curso=curso).exists() if request.user.is_authenticated else False

    return render(request, 'cursos/detalle_Cursos.html', {
        'curso': curso,
        'inscripciones': inscripciones,
        'es_profesor': es_profesor,
        'esta_inscrito': esta_inscrito
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

def subir_material_extra(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    if request.method == 'POST':
        form = MaterialExtraForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.curso = curso
            material.profesor = Profesor.objects.get(user=request.user)
            material.save()

            # 🔥 Crear Recurso automáticamente
            Recurso.objects.create(
                titulo=material.titulo,
                descripcion=material.descripcion,
                tipo_archivo="Archivo",
                enlace=material.archivo.url,
                curso=curso
            )

            return redirect('subir_material_extra', curso_id=curso.id)
    else:
        form = MaterialExtraForm()

    material_extra = MaterialExtra.objects.filter(curso=curso)

    return render(request, 'cursos/subir_material_extra.html', {
        'curso': curso,
        'form': form,
        'material_extra': material_extra,
    })




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
        progreso_por_curso[inscripcion.curso.id] = {
            'curso': inscripcion.curso,
            'porcentaje': round(porcentaje, 2),
            'total': total,
            'completados': completados,
            'recursos': recursos,
            'completados_ids': list(progresos.filter(inscripcion=inscripcion, completado=True).values_list('recurso_id', flat=True))
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

#EXTRAS
#Darse de baja de curso
from django.contrib import messages

@login_required
def darse_de_baja_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripcion = Inscripcion.objects.filter(user=request.user, curso=curso).first()

    if not inscripcion:
        messages.error(request, "No estás inscrito en este curso.")
        return redirect('detalle_curso', curso_id=curso.id)

    if request.method == 'POST':
        inscripcion.delete()
        messages.success(request, f"Te has dado de baja del curso '{curso.titulo}'.")
        return redirect('lista_cursos')

    return render(request, 'cursos/confirmar_baja.html', {'curso': curso})



#maestro vea a sus estudiantes con el progreso
@login_required
def dashboard(request):
    if hasattr(request.user, 'profesor'):
        profesor = request.user.profesor
        cursos = Curso.objects.filter(profesor=profesor)
        cursos_con_inscripciones = []

        for curso in cursos:
            inscripciones = Inscripcion.objects.filter(curso=curso)

            # Para cada inscripción, obtener progreso de ese estudiante en ese curso
            estudiantes_con_progreso = []
            for inscripcion in inscripciones:
                total_recursos = Recurso.objects.filter(curso=curso).count()
                completados = Progreso.objects.filter(inscripcion=inscripcion, completado=True).count()
                porcentaje = (completados / total_recursos * 100) if total_recursos > 0 else 0

                estudiantes_con_progreso.append({
                    'inscripcion': inscripcion,
                    'progreso': round(porcentaje, 2),
                    'total_recursos': total_recursos,
                    'completados': completados,
                })

            cursos_con_inscripciones.append({
                'curso': curso,
                'estudiantes': estudiantes_con_progreso,
            })

        return render(request, 'cursos/dashboard_profesor.html', {
            'cursos_con_inscripciones': cursos_con_inscripciones
        })
    else:
        return redirect('lista_cursos')

# Funciones y vistas para el perfil de usuario (profesor y estudiante)
    # Esto es para ver si el usuario es un profesor
    
def es_profesor(user):
    return hasattr(user, 'profesor')

def perfil_usuario(request):
    user = request.user

    if es_profesor(user):
        
        profesor = user.profesor
        cursos = Curso.objects.filter(profesor=profesor)

        return render(request, 'cursos/perfil.html', {
            'es_profesor':True,
            'profesor': profesor,
            'cursos': cursos
        })

    else:
        inscripciones = Inscripcion.objects.filter(user=user)
        cursos_info = []
        progresos = Progreso.objects.filter(inscripcion__in=inscripciones).select_related('recurso', 'inscripcion', 'inscripcion__curso')
        
        for insc in inscripciones:
            recursos = Recurso.objects.filter(curso=insc.curso)
            progreso_dict = {
                p.recurso.id: p.completado
                for p in Progreso.objects.filter(inscripcion=insc)
            }
            
            materiales = []
            for recurso in recursos:
                estado = 'completado' if progreso_dict.get(recurso.id) else 'incompleto'
                materiales.append({
                    'titulo': recurso.titulo,
                    'estado': estado,
                    'id':recurso.id
                })
                
            completados = progresos.filter(inscripcion=insc, completado=True).count()
            total = recursos.count()

            porcentaje = round((completados / total * 100), 2) if total > 0 else 0
            cursos_info.append({
                'titulo_curso': insc.curso.titulo,
                'materiales': materiales,
                'porcentaje':porcentaje,
            })

        return render(request, 'cursos/perfil.html', {
            'es_profesor':False,
            'cursos_info': cursos_info
        })
