from django.db import models
from django.contrib.auth.models import User

# Create your models here.
  #  ---- MODELOS DE LA APLICACION ----
from django.db import models

class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #Relacion de usuario para que el maestro tenga una sesion igual al estudiante
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Inscripcion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    nombre_estudiante = models.CharField(max_length=100)
    email_estudiante = models.EmailField()
    fecha_inscripcion = models.DateField(auto_now_add=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username if self.user else self.nombre_estudiante} - {self.curso.titulo}"

class Recurso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_archivo = models.CharField(max_length=50)
    enlace = models.URLField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Progreso(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.inscripcion.nombre_estudiante} - {self.recurso.titulo}"

 # Modelo para el material extra de los cursos
class MaterialExtra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)  # Relaciona el material extra con un curso
    archivo = models.FileField(upload_to='materiales_extra/')
    descripcion = models.TextField(blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
