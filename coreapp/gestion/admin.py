from django.contrib import admin
from .models import Rol, Curso, Inscripcion

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre','modalidad','fecha_inicio','fecha_fin','cupo')

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario','curso','fecha_inscripcion','estado')
    list_filter  = ('estado',)
