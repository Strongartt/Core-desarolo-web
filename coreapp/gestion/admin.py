from django.contrib import admin
from .models import Rol, Curso, Inscripcion, CategoriaCurso, PlanMembresia, Trimestre

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

@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    
@admin.register(PlanMembresia)
class PlanMembresiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'limite_precio_curso')

@admin.register(Trimestre)
class TrimestreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin')