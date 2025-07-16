from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# ----- ROLES Y PERFIL -----

class Rol(models.Model):
    codigo = models.CharField(max_length=10, unique=True)  # Ej: ADMIN, DOC, EST
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre



class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    plan_membresia = models.ForeignKey('PlanMembresia', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio_membresia = models.DateField(null=True, blank=True)
    fecha_fin_membresia = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.rol.codigo})'

    def membresia_activa(self):
        hoy = timezone.now().date()
        if not self.plan_membresia:
            return False

        if self.plan_membresia.nombre.lower() == 'gratuita':
            return True  # Gratuita no caduca

        return (
            self.fecha_inicio_membresia is not None and
            self.fecha_fin_membresia is not None and
            self.fecha_inicio_membresia <= hoy <= self.fecha_fin_membresia
        )

        

    def get_plan_actual(self):
        from .models import PlanMembresia

        if self.plan_membresia and self.plan_membresia.nombre.lower() == 'gratuita':
            return self.plan_membresia

        if self.membresia_activa():
            return self.plan_membresia

        return PlanMembresia.objects.filter(nombre__iexact="Gratuita").first()




# ----- CURSO -----
class CategoriaCurso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

MODALIDADES = [
    ('PRESENCIAL', 'Presencial'),
    ('ONLINE', 'En línea'),
]

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    modalidad = models.CharField(max_length=20, choices=MODALIDADES)
    trimestre = models.ForeignKey('Trimestre', on_delete=models.SET_NULL, null=True, blank=True)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cupo = models.PositiveIntegerField()
    docente = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'rol__codigo': 'DOC'})
    categoria = models.ForeignKey(CategoriaCurso, on_delete=models.CASCADE, null=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nombre

    @property
    def cupos_disponibles(self):
        return self.cupo - self.inscripcion_set.count()

    @property
    def membresia_requerida(self):
        if self.precio == 0:
            return "Gratuita"
        elif self.precio <= 20:
            return "Básica"
        else:
            return "Premium"





# ----- INSCRIPCION -----

ESTADOS_INSCRIPCION = [
    ('INSCRITO', 'Inscrito'),
    ('APROBADO', 'Aprobado'),
    ('REPROBADO', 'Reprobado'),
    ('RETIRADO', 'Retirado'),
]

class Inscripcion(models.Model):
    
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_INSCRIPCION, default='INSCRITO')
    nota_final = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    asistencia_total = models.PositiveIntegerField(default=0)
    codigo_certificado = models.CharField(max_length=100, blank=True, null=True)
    fecha_certificado = models.DateField(blank=True, null=True)
    
    SOLICITUD_BAJA_CHOICES = [
        ('NINGUNA', 'Ninguna'),
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    solicitud_baja = models.CharField(
        max_length=10,
        choices=SOLICITUD_BAJA_CHOICES,
        default='NINGUNA'
    )


    def __str__(self):
        return f'{self.usuario.get_full_name()} en {self.curso}'


# ----- SESIONES DE ASISTENCIA -----

class SesionAsistencia(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    fecha = models.DateField()
    presente = models.BooleanField(default=False)

    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        return f'{self.inscripcion.usuario.get_full_name()} - {estado} ({self.fecha})'


# ----- EVALUACIONES -----

class Evaluacion(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    nota = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f'{self.titulo} - {self.inscripcion.usuario.get_full_name()}'

@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'perfil'):
        # Asignar rol estudiante por defecto (ajusta si necesitas otro)
        rol_defecto = Rol.objects.filter(codigo='EST').first()
        if rol_defecto:
            Perfil.objects.create(user=instance, rol=rol_defecto)
            

class PlanMembresia(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: Gratuita, Básica, Premium
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)  # Precio mensual
    limite_precio_curso = models.DecimalField(max_digits=6, decimal_places=2)  # Máximo curso accesible

    def __str__(self):
        return f"{self.nombre} (${self.precio}) - Hasta cursos de ${self.limite_precio_curso}"
   
class Trimestre(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return self.nombre    