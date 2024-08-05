from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

############################################
       ###PERFILES###
############################################
class Perfil(models.Model):
    USUARIO_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('administrador', 'Administrador'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True, null=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True, null=True)
    email =  models.EmailField(unique=True)
    telefono = models.CharField(max_length=10)
    tipo_usuario = models.CharField(max_length=20, choices=USUARIO_CHOICES)
    fecha_nacimiento = models.DateField()

    def save(self, *args, **kwargs):
        if self.es_menor_de_edad() and self.tipo_usuario in ['profesor', 'administrador']:
            raise ValueError("Los menores de edad no pueden ser profesores o administradores.")
        super().save(*args, **kwargs)

    def es_menor_de_edad(self):
        from datetime import date
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return edad < 18

    def __str__(self):
        nombres = [self.primer_nombre]
        if self.segundo_nombre:
            nombres.append(self.segundo_nombre)
        apellidos = [self.primer_apellido]
        if self.segundo_apellido:
            apellidos.append(self.segundo_apellido)
        nombre_completo = " ".join(nombres + apellidos)
        return f"Perfil de {self.user.username}"


############################################
       ###ALUMNOS###
############################################
class Alumno(models.Model):
    GRADO_GRUPO_CHOICES = (
        ('1a', '1A'),
        ('1b', '1B'),
        ('2a', '2A'),
        ('2b', '2B'),
        ('3a', '3A'),
        ('3b', '3B'),
    )

    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'estudiante'})
    grado_grupo = models.CharField(max_length=2, choices=GRADO_GRUPO_CHOICES)

    def __str__(self):
        return f"Alumno {self.perfil.primer_nombre} {self.perfil.primer_apellido} - {self.grado_grupo}"


############################################
       ###Profesor###
############################################
class Maestro(models.Model):
    MATERIA_CHOICES = (
        ('matemáticas 1', 'Matemáticas 1'),
        ('matemáticas 2', 'Matemáticas 2'),
        ('matemáticas 3', 'Matemáticas 3'),
        ('español 1', 'Español 1'),
        ('español 2', 'Español 2'),
        ('español 3', 'Español 3'),
        ('ciencias 1', 'Ciencias 1'),
        ('ciencias 2', 'Ciencias 2'),
        ('ciencias 3', 'Ciencias 3'),
    )

    GRADO_GRUPO_CHOICES = (
        ('1a', '1A'),
        ('1b', '1B'),
        ('2a', '2A'),
        ('2b', '2B'),
        ('3a', '3A'),
        ('3b', '3B'),
    )

    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'profesor'})
    materia = models.CharField(max_length=20, choices=MATERIA_CHOICES)
    grupo = models.CharField(max_length=2, choices=GRADO_GRUPO_CHOICES)

    def __str__(self):
        return f"Maestro {self.perfil.primer_nombre} {self.perfil.primer_apellido} - {self.materia} - {self.grupo}"


############################################
       ###Calificaciones###
############################################
class Calificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Maestro, on_delete=models.CASCADE, limit_choices_to={'perfil__tipo_usuario': 'profesor'})
    calificacion1 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    calificacion2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    calificacion3 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    calificacion_final = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.alumno.grado_grupo != self.materia.grupo:
            raise ValueError("El profesor solo puede calificar a los alumnos que están en su mismo grupo.")
        
        if self.calificacion1 is not None and self.calificacion2 is not None and self.calificacion3 is not None:
            self.calificacion_final = (self.calificacion1 + self.calificacion2 + self.calificacion3) / 3
        else:
            self.calificacion_final = None

        if not self.can_modify(self.materia.perfil.user):
            raise PermissionDenied("No tienes permiso para modificar esta calificación.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Calificación de {self.alumno.perfil.primer_nombre} {self.alumno.perfil.primer_apellido} en {self.materia.materia}"

    def can_modify(self, user):
        return user.perfil.tipo_usuario == 'administrador' or (
            user.perfil.tipo_usuario == 'profesor' and self.materia.perfil == user.perfil
        )