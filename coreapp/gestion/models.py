from django.db import models

class Rol(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    nombre   = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email    = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    rol      = models.ForeignKey(Rol, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Curso(models.Model):
    nombre       = models.CharField(max_length=100)
    modalidad    = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField()
    cupo         = models.PositiveIntegerField()
    def __str__(self):
        return self.nombre

class Inscripcion(models.Model):
    usuario            = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    curso              = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion  = models.DateField(auto_now_add=True)
    estado             = models.CharField(max_length=20)
    nota_final         = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    asistencia_total   = models.PositiveIntegerField(default=0)
    codigo_certificado = models.CharField(max_length=100, blank=True, null=True)
    fecha_certificado  = models.DateField(blank=True, null=True)
    def __str__(self):
        return f'{self.usuario} en {self.curso}'
